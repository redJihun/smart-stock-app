from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Literal

import pandas as pd

from smart_stock.data.schema import (
    FDR_COLUMN_MAP,
    YFINANCE_COLUMN_MAP,
    normalize_columns,
)
from smart_stock.utils.date_utils import (
    DateLike,
    date_range_str,
    default_end_date,
    default_start_date,
)

if TYPE_CHECKING:
    from typing import TypeAlias

    Interval: TypeAlias = Literal["1d", "1h", "30m", "15m", "5m", "1m"]


class Market(StrEnum):
    """시장 구분."""

    KR = "KR"  # 국내 (fdr)
    US = "US"  # 미국 (yfinance)
    GLOBAL = "GLOBAL"  # 기타 해외 (yfinance)


def fetch_stock(
    ticker: str,
    start: DateLike | None = None,
    end: DateLike | None = None,
    *,
    market: Market = Market.KR,
    interval: str = "1d",
) -> pd.DataFrame:
    """주식 데이터를 조회하여 표준 DataFrame으로 반환한다.

    Parameters
    ----------
    ticker : str
        종목 코드 (국내: '005930', 해외: 'AAPL')
    start : DateLike | None
        시작일 (기본: 1년 전)
    end : DateLike | None
        종료일 (기본: 오늘)
    market : Market
        시장 구분. KR=국내(fdr), US/GLOBAL=해외(yfinance)
    interval : str
        시간 단위. "1d" | "1h" | "30m" | "15m" | "5m" | "1m"

    Returns
    -------
    pd.DataFrame
        DatetimeIndex, columns=[Open, High, Low, Close, Volume]
    """
    start_date = default_start_date() if start is None else start
    end_date = default_end_date() if end is None else end
    start_str, end_str = date_range_str(start_date, end_date)

    if market == Market.KR:
        return _fetch_kr(ticker, start_str, end_str, interval=interval)
    return _fetch_foreign(ticker, start_str, end_str, interval=interval)


def _fetch_kr(
    ticker: str, start_str: str, end_str: str, interval: str = "1d"
) -> pd.DataFrame:
    """한국 주식 데이터 조회.

    일봉(1d)은 fdr.DataReader 호출, 분봉은 KIS API 호출.

    Parameters
    ----------
    ticker : str
        종목 코드
    start_str : str
        시작일 (YYYY-MM-DD)
    end_str : str
        종료일 (YYYY-MM-DD)
    interval : str
        시간 단위. "1d" | "1h" | "30m" | "15m" | "5m" | "1m"

    Returns
    -------
    pd.DataFrame
        표준 OHLCV 컬럼 + DatetimeIndex
    """
    if interval == "1d":
        import FinanceDataReader as fdr  # noqa: N813, PLC0415

        raw: pd.DataFrame = fdr.DataReader(ticker, start_str, end_str)
        return normalize_columns(raw, FDR_COLUMN_MAP)

    from smart_stock.data.kis_client import fetch_kr_intraday  # noqa: PLC0415

    # 분봉 조회 (start_str ~ end_str 범위, interval 단위)
    dfs = []
    current = pd.Timestamp(start_str)
    end = pd.Timestamp(end_str)

    while current <= end:
        date_yyyymmdd = current.strftime("%Y%m%d")
        try:
            df = fetch_kr_intraday(ticker, date_yyyymmdd, interval=interval)
            if not df.empty:
                dfs.append(df)
        except Exception:  # noqa: BLE001
            # 데이터 없는 날은 건너뜀
            pass
        current += pd.Timedelta(days=1)

    if not dfs:
        # 데이터 없으면 빈 DataFrame 반환
        return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    result = pd.concat(dfs, ignore_index=False)
    return result.sort_index()


def _fetch_foreign(
    ticker: str, start_str: str, end_str: str, interval: str = "1d"
) -> pd.DataFrame:
    """해외 주식 데이터 조회.

    yfinance.download 호출 후 표준 컬럼으로 정규화한다.

    Parameters
    ----------
    ticker : str
        종목 코드
    start_str : str
        시작일 (YYYY-MM-DD)
    end_str : str
        종료일 (YYYY-MM-DD)
    interval : str
        시간 단위. "1d" | "1h" | "30m" | "15m" | "5m" | "1m"

    Returns
    -------
    pd.DataFrame
        표준 OHLCV 컬럼 + DatetimeIndex
    """
    import yfinance as yf  # noqa: PLC0415

    raw: pd.DataFrame = yf.download(
        ticker,
        start=start_str,
        end=end_str,
        interval=interval,
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
    )
    return normalize_columns(raw, YFINANCE_COLUMN_MAP)
