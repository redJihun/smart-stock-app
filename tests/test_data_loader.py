from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from smart_stock.data.loader import Market, _fetch_foreign, _fetch_kr, fetch_stock
from smart_stock.data.schema import (
    STANDARD_COLUMNS,
    normalize_columns,
    validate_schema,
)
from smart_stock.utils.date_utils import (
    date_range_str,
    default_end_date,
    default_start_date,
    to_date,
    to_date_str,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_ohlcv(rows: int = 3) -> pd.DataFrame:
    """Open/High/Low/Close/Volume 컬럼을 가진 샘플 DataFrame."""
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    return pd.DataFrame(
        {
            "Open": [70000.0] * rows,
            "High": [71000.0] * rows,
            "Low": [69000.0] * rows,
            "Close": [70500.0] * rows,
            "Volume": [1_000_000] * rows,
        },
        index=idx,
    )


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return _make_ohlcv()


# ---------------------------------------------------------------------------
# date_utils
# ---------------------------------------------------------------------------


def test_to_date_from_iso_str() -> None:
    assert to_date("2024-01-15") == date(2024, 1, 15)


def test_to_date_from_compact_str() -> None:
    assert to_date("20240115") == date(2024, 1, 15)


def test_to_date_from_date() -> None:
    d = date(2024, 1, 15)
    assert to_date(d) is d


def test_to_date_str_default_fmt() -> None:
    assert to_date_str("20240115") == "2024-01-15"


def test_date_range_str_returns_tuple() -> None:
    start, end = date_range_str("2024-01-01", "2024-12-31")
    assert start == "2024-01-01"
    assert end == "2024-12-31"


def test_default_end_date_is_today() -> None:
    assert default_end_date() == date.today()


def test_default_start_date_is_1_year_ago() -> None:
    today = date.today()
    result = default_start_date(1)
    assert result.year == today.year - 1


# ---------------------------------------------------------------------------
# schema
# ---------------------------------------------------------------------------


def test_validate_schema_passes(sample_df: pd.DataFrame) -> None:
    assert validate_schema(sample_df) is True


def test_validate_schema_fails_missing_column(sample_df: pd.DataFrame) -> None:
    df = sample_df.drop(columns=["Volume"])
    assert validate_schema(df) is False


def test_normalize_columns_renames_correctly() -> None:
    df = pd.DataFrame(
        {"Open": [1.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [100]}
    )
    column_map = {c: c for c in ["Open", "High", "Low", "Close", "Volume"]}
    result = normalize_columns(df, column_map)
    assert list(result.columns) == STANDARD_COLUMNS


def test_normalize_columns_drops_extra_columns() -> None:
    df = pd.DataFrame(
        {
            "Open": [1.0],
            "High": [2.0],
            "Low": [0.5],
            "Close": [1.5],
            "Volume": [100],
            "Extra": [999],
        }
    )
    cols = ["Open", "High", "Low", "Close", "Volume"]
    result = normalize_columns(df, {c: c for c in cols})
    assert "Extra" not in result.columns


# ---------------------------------------------------------------------------
# loader — fetch_stock 라우팅
# ---------------------------------------------------------------------------


def test_fetch_stock_kr_routes_to_fetch_kr(sample_df: pd.DataFrame) -> None:
    with patch("smart_stock.data.loader._fetch_kr", return_value=sample_df) as mock_kr:
        result = fetch_stock("005930", "2024-01-01", "2024-12-31", market=Market.KR)
        mock_kr.assert_called_once_with(
            "005930", "2024-01-01", "2024-12-31", interval="1d"
        )
    assert validate_schema(result)


def test_fetch_stock_us_routes_to_fetch_foreign(sample_df: pd.DataFrame) -> None:
    target = "smart_stock.data.loader._fetch_foreign"
    with patch(target, return_value=sample_df) as mock_foreign:
        result = fetch_stock("AAPL", "2024-01-01", "2024-12-31", market=Market.US)
        mock_foreign.assert_called_once_with(
            "AAPL", "2024-01-01", "2024-12-31", interval="1d"
        )
    assert validate_schema(result)


def test_fetch_stock_global_routes_to_fetch_foreign(sample_df: pd.DataFrame) -> None:
    target = "smart_stock.data.loader._fetch_foreign"
    with patch(target, return_value=sample_df) as mock_foreign:
        fetch_stock("7203.T", "2024-01-01", "2024-12-31", market=Market.GLOBAL)
        mock_foreign.assert_called_once()


def test_fetch_stock_default_dates_applied(sample_df: pd.DataFrame) -> None:
    """start/end 미지정 시 기본값이 자동 적용되어야 한다."""
    with patch("smart_stock.data.loader._fetch_kr", return_value=sample_df) as mock_kr:
        fetch_stock("005930")
        args = mock_kr.call_args[0]
        # args[1]=start_str, args[2]=end_str 이 date 형식이어야 함
        assert args[1] == default_start_date().strftime("%Y-%m-%d")
        assert args[2] == default_end_date().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# loader — _fetch_kr / _fetch_foreign (fdr, yfinance mock)
# ---------------------------------------------------------------------------


def test_fetch_kr_calls_fdr_datareader(sample_df: pd.DataFrame) -> None:
    mock_fdr = MagicMock()
    mock_fdr.DataReader.return_value = sample_df
    with patch.dict("sys.modules", {"FinanceDataReader": mock_fdr}):
        result = _fetch_kr("005930", "2024-01-01", "2024-12-31")
    mock_fdr.DataReader.assert_called_once_with("005930", "2024-01-01", "2024-12-31")
    assert validate_schema(result)


def test_fetch_foreign_calls_yfinance_download(sample_df: pd.DataFrame) -> None:
    mock_yf = MagicMock()
    mock_yf.download.return_value = sample_df
    with patch.dict("sys.modules", {"yfinance": mock_yf}):
        result = _fetch_foreign("AAPL", "2024-01-01", "2024-12-31")
    mock_yf.download.assert_called_once()
    assert validate_schema(result)


# ---------------------------------------------------------------------------
# loader — interval 파라미터 (분봉 데이터)
# ---------------------------------------------------------------------------


def test_fetch_stock_kr_intraday_calls_kis(sample_df: pd.DataFrame) -> None:
    """interval="5m" 시 _fetch_kr이 kis_client 호출 경로를 사용한다."""
    # 분봉 데이터는 kis_client를 통해 조회되므로,
    # kis_client.fetch_kr_intraday이 호출되는지 확인
    with patch("smart_stock.data.kis_client.fetch_kr_intraday") as mock_kis:
        mock_kis.return_value = sample_df

        result = _fetch_kr("005930", "2024-01-01", "2024-01-01", interval="5m")
        # kis_client.fetch_kr_intraday가 호출되어야 함
        mock_kis.assert_called_once()
        assert validate_schema(result)


def test_fetch_stock_foreign_interval_passed(sample_df: pd.DataFrame) -> None:
    """interval이 yf.download에 전달되는지 확인."""
    mock_yf = MagicMock()
    mock_yf.download.return_value = sample_df
    with patch.dict("sys.modules", {"yfinance": mock_yf}):
        _fetch_foreign("AAPL", "2024-01-01", "2024-12-31", interval="1h")
    # interval 파라미터가 전달되었는지 확인
    call_kwargs = mock_yf.download.call_args[1]
    assert call_kwargs.get("interval") == "1h"


def test_cache_path_includes_interval() -> None:
    """cache_path 파일명에 interval이 포함되는지 검증한다."""
    from smart_stock.data.cache import cache_path

    path = cache_path("005930", "KR", "2024-01-01", "2024-12-31", "5m")
    assert "5m" in path.name


def test_fetch_stock_cached_interval_default() -> None:
    """fetch_stock_cached의 interval 기본값이 '1d'인지 검증한다."""
    from inspect import signature

    from smart_stock.data.cache import fetch_stock_cached

    sig = signature(fetch_stock_cached)
    assert sig.parameters["interval"].default == "1d"
