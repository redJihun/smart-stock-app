from typing import Final

import pandas as pd

# 표준 컬럼명 상수
COL_OPEN: Final = "Open"
COL_HIGH: Final = "High"
COL_LOW: Final = "Low"
COL_CLOSE: Final = "Close"
COL_VOLUME: Final = "Volume"

STANDARD_COLUMNS: Final[list[str]] = [
    COL_OPEN,
    COL_HIGH,
    COL_LOW,
    COL_CLOSE,
    COL_VOLUME,
]

# fdr은 이미 Open/High/Low/Close/Volume을 사용하므로 동일 매핑
FDR_COLUMN_MAP: dict[str, str] = {
    "Open": COL_OPEN,
    "High": COL_HIGH,
    "Low": COL_LOW,
    "Close": COL_CLOSE,
    "Volume": COL_VOLUME,
}

# yfinance는 컬럼명이 동일하나 MultiIndex 처리 후 동일 형태로 맞춤
YFINANCE_COLUMN_MAP: dict[str, str] = {
    "Open": COL_OPEN,
    "High": COL_HIGH,
    "Low": COL_LOW,
    "Close": COL_CLOSE,
    "Volume": COL_VOLUME,
}


def normalize_columns(df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    """컬럼명을 표준 스키마로 정규화하고 표준 컬럼만 추출한다."""
    df = df.rename(columns=column_map)
    available = [col for col in STANDARD_COLUMNS if col in df.columns]
    return df[available].copy()


def validate_schema(df: pd.DataFrame) -> bool:
    """표준 컬럼 5개가 모두 존재하는지 검증한다."""
    return all(col in df.columns for col in STANDARD_COLUMNS)
