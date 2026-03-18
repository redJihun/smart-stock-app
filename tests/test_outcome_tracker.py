"""OutcomeTracker 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.tracking.tracker import OutcomeTracker


def _make_signals_df() -> pd.DataFrame:
    """테스트용 시그널 DataFrame."""
    return pd.DataFrame(
        [
            {
                "strategy_name": "TestStrategy",
                "ticker": "005930",
                "signal_date": pd.Timestamp("2024-01-10"),
                "signal": 1,
                "price": 70000.0,
                "logged_at": pd.Timestamp("2024-01-10 09:00"),
            }
        ]
    )


def _make_price_series(
    base_date: str, n: int = 10, base_price: float = 70000.0
) -> pd.DataFrame:
    """mock fetcher가 반환할 샘플 가격 DataFrame."""
    idx = pd.date_range(base_date, periods=n, freq="B")
    prices = [base_price * (1 + 0.01 * i) for i in range(n)]
    return pd.DataFrame({"Close": prices}, index=idx)


class TestOutcomeTrackerLoad:
    def test_load_empty_before_update(self, tmp_path: Path) -> None:
        """파일 없으면 빈 DataFrame 반환."""
        tracker = OutcomeTracker(log_dir=tmp_path)
        df = tracker.load()
        assert df.empty


class TestOutcomeTrackerUpdate:
    def test_update_returns_dataframe(self, tmp_path: Path) -> None:
        """update() 반환 타입이 DataFrame."""
        mock_fetcher = MagicMock(return_value=_make_price_series("2024-01-09", n=10))
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        result = tracker.update(_make_signals_df())
        assert isinstance(result, pd.DataFrame)

    def test_outcome_1d_calculation(self, tmp_path: Path) -> None:
        """1 영업일 후 수익률이 정확히 계산됨."""
        # entry_price=70000, 1일 후 가격=70700 → 1.0%
        prices = _make_price_series("2024-01-09", n=10, base_price=70000.0)
        mock_fetcher = MagicMock(return_value=prices)
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        result = tracker.update(_make_signals_df())
        # signal_date=2024-01-10, future[0]는 2024-01-11 가격
        assert result.iloc[0]["outcome_1d"] is not None

    def test_outcome_1w_calculation(self, tmp_path: Path) -> None:
        """5 영업일 후 수익률이 None이 아님 (데이터 충분한 경우)."""
        prices = _make_price_series("2024-01-09", n=15, base_price=70000.0)
        mock_fetcher = MagicMock(return_value=prices)
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        result = tracker.update(_make_signals_df())
        assert result.iloc[0]["outcome_1w"] is not None

    def test_outcome_none_when_no_future_data(self, tmp_path: Path) -> None:
        """미래 데이터가 없으면 outcome_1d = None."""
        # signal_date 이후 데이터가 없는 케이스
        empty_prices = pd.DataFrame({"Close": []}, index=pd.DatetimeIndex([]))
        mock_fetcher = MagicMock(return_value=empty_prices)
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        result = tracker.update(_make_signals_df())
        assert result.iloc[0]["outcome_1d"] is None
        assert result.iloc[0]["outcome_1w"] is None

    def test_update_saves_to_parquet(self, tmp_path: Path) -> None:
        """update() 후 outcomes.parquet 파일이 생성됨."""
        mock_fetcher = MagicMock(return_value=_make_price_series("2024-01-09"))
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        tracker.update(_make_signals_df())
        assert (tmp_path / "outcomes.parquet").exists()

    def test_fetcher_called_per_ticker(self, tmp_path: Path) -> None:
        """ticker별로 fetcher가 호출됨."""
        mock_fetcher = MagicMock(return_value=_make_price_series("2024-01-09"))
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=mock_fetcher)
        tracker.update(_make_signals_df())
        mock_fetcher.assert_called_once()

    def test_custom_fetcher_injection(self, tmp_path: Path) -> None:
        """주입된 mock fetcher가 실제로 사용됨 (외부 의존성 격리)."""
        custom_fetcher = MagicMock(return_value=_make_price_series("2024-01-09"))
        tracker = OutcomeTracker(log_dir=tmp_path, fetcher=custom_fetcher)
        tracker.update(_make_signals_df())
        assert custom_fetcher.called
