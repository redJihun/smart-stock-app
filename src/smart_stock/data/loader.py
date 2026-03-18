from enum import StrEnum

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
) -> pd.DataFrame:
    """주식 일봉 데이터를 조회하여 표준 DataFrame으로 반환한다.

    Args:
        ticker: 종목 코드 (국내: '005930', 해외: 'AAPL')
        start:  시작일 (기본: 1년 전)
        end:    종료일 (기본: 오늘)
        market: KR=국내(fdr), US/GLOBAL=해외(yfinance)

    Returns:
        DatetimeIndex, columns=[Open, High, Low, Close, Volume]
    """
    start_date = default_start_date() if start is None else start
    end_date = default_end_date() if end is None else end
    start_str, end_str = date_range_str(start_date, end_date)

    if market == Market.KR:
        return _fetch_kr(ticker, start_str, end_str)
    return _fetch_foreign(ticker, start_str, end_str)


def _fetch_kr(ticker: str, start_str: str, end_str: str) -> pd.DataFrame:
    """fdr.DataReader 호출 후 표준 컬럼으로 정규화한다."""
    import FinanceDataReader as fdr  # noqa: N813, PLC0415

    raw: pd.DataFrame = fdr.DataReader(ticker, start_str, end_str)
    return normalize_columns(raw, FDR_COLUMN_MAP)


def _fetch_foreign(ticker: str, start_str: str, end_str: str) -> pd.DataFrame:
    """yfinance.download 호출 후 표준 컬럼으로 정규화한다."""
    import yfinance as yf  # noqa: PLC0415

    raw: pd.DataFrame = yf.download(
        ticker,
        start=start_str,
        end=end_str,
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
    )
    return normalize_columns(raw, YFINANCE_COLUMN_MAP)
