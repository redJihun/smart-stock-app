from __future__ import annotations

from pathlib import Path

import pandas as pd

from smart_stock.data.loader import Market, fetch_stock
from smart_stock.utils.date_utils import (
    DateLike,
    default_end_date,
    default_start_date,
    to_date_str,
)

DEFAULT_CACHE_DIR = Path("data/raw")


def cache_path(
    ticker: str,
    market: str,
    start: str,
    end: str,
    interval: str = "1d",
) -> Path:
    """캐시 파일 경로를 생성한다.

    Parameters
    ----------
    ticker : str
        종목 코드
    market : str
        시장 구분 (예: "KR", "US")
    start : str
        시작일 (YYYY-MM-DD 형식)
    end : str
        종료일 (YYYY-MM-DD 형식)
    interval : str
        분봉 단위 (기본값: "1d")

    Returns
    -------
    Path
        캐시 파일 경로

    Examples
    --------
    >>> cache_path("005930", "KR", "2024-01-01", "2024-12-31", "1d")
    Path('data/raw/KR_005930_20240101_20241231_1d.parquet')

    >>> cache_path("005930", "KR", "2024-01-01", "2024-01-02", "5m")
    Path('data/raw/KR_005930_20240101_20240102_5m.parquet')
    """
    start_compact = start.replace("-", "")
    end_compact = end.replace("-", "")
    filename = f"{market}_{ticker}_{start_compact}_{end_compact}_{interval}.parquet"
    return DEFAULT_CACHE_DIR / filename


def save_cache(df: pd.DataFrame, path: Path) -> None:
    """DataFrame을 Parquet 파일로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)


def load_cache(path: Path) -> pd.DataFrame | None:
    """캐시 파일이 있으면 로드하고, 없으면 None을 반환한다."""
    if not path.exists():
        return None
    return pd.read_parquet(path)


def fetch_stock_cached(
    ticker: str,
    start: DateLike | None = None,
    end: DateLike | None = None,
    *,
    market: Market = Market.KR,
    interval: str = "1d",
    cache_dir: Path = DEFAULT_CACHE_DIR,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """캐시를 우선 조회하고, 없으면 fetch_stock을 호출한 뒤 저장한다.

    Parameters
    ----------
    ticker : str
        종목 코드
    start : DateLike | None
        시작일 (기본: 1년 전)
    end : DateLike | None
        종료일 (기본: 오늘)
    market : Market
        시장 구분 (기본값: Market.KR)
    interval : str
        분봉 단위 (기본값: "1d")
    cache_dir : Path
        캐시 디렉토리 (테스트 시 tmp_path 주입 가능)
    force_refresh : bool
        True이면 캐시를 무시하고 새로 조회

    Returns
    -------
    pd.DataFrame
        DatetimeIndex, columns=[Open, High, Low, Close, Volume]
    """
    start_date = default_start_date() if start is None else start
    end_date = default_end_date() if end is None else end
    start_str = to_date_str(start_date)
    end_str = to_date_str(end_date)

    path = (
        cache_dir / cache_path(ticker, market.value, start_str, end_str, interval).name
    )

    if not force_refresh:
        cached = load_cache(path)
        if cached is not None:
            return cached

    df = fetch_stock(ticker, start_str, end_str, market=market, interval=interval)
    save_cache(df, path)
    return df
