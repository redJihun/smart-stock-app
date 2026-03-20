"""대시보드 데이터 처리 모듈."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DEFAULT_LOG_DIR = Path("data/tracking")


def load_signals(log_dir: Path = DEFAULT_LOG_DIR) -> pd.DataFrame:
    """signals.parquet 로드.

    Parameters
    ----------
    log_dir : Path
        데이터 디렉토리 (기본값: data/tracking)

    Returns
    -------
    pd.DataFrame
        시그널 데이터. 파일 없으면 빈 DataFrame.
    """
    path = log_dir / "signals.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_outcomes(log_dir: Path = DEFAULT_LOG_DIR) -> pd.DataFrame:
    """outcomes.parquet 로드.

    Parameters
    ----------
    log_dir : Path
        데이터 디렉토리 (기본값: data/tracking)

    Returns
    -------
    pd.DataFrame
        결과 데이터. 파일 없으면 빈 DataFrame.
    """
    path = log_dir / "outcomes.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@dataclass
class DashboardMetrics:
    """대시보드 요약 지표.

    Attributes
    ----------
    total_signals : int
        총 시그널 수
    win_rate_1d : float | None
        1일 적중률 (outcome_1d > 0 비율). 데이터 없으면 None.
    win_rate_1w : float | None
        1주 적중률. 데이터 없으면 None.
    avg_return_1d : float | None
        1일 평균 수익률. 데이터 없으면 None.
    avg_return_1w : float | None
        1주 평균 수익률. 데이터 없으면 None.
    """

    total_signals: int
    win_rate_1d: float | None
    win_rate_1w: float | None
    avg_return_1d: float | None
    avg_return_1w: float | None


def compute_metrics(outcomes_df: pd.DataFrame) -> DashboardMetrics:
    """outcomes DataFrame → DashboardMetrics.

    Parameters
    ----------
    outcomes_df : pd.DataFrame
        결과 데이터 (outcome_1d, outcome_1w 컬럼 포함)

    Returns
    -------
    DashboardMetrics
        계산된 지표 집합

    Notes
    -----
    outcomes_df가 비었으면 total_signals=0, 나머지 None 반환.
    적중률: outcome_Xd > 0 인 비율 (방향 예측 정확도).
    """
    if outcomes_df.empty:
        return DashboardMetrics(
            total_signals=0,
            win_rate_1d=None,
            win_rate_1w=None,
            avg_return_1d=None,
            avg_return_1w=None,
        )

    total = len(outcomes_df)

    # 1d 지표
    col_1d = "outcome_1d"
    win_rate_1d: float | None = None
    avg_return_1d: float | None = None
    if col_1d in outcomes_df.columns:
        valid_1d = outcomes_df[col_1d].dropna()
        if len(valid_1d) > 0:
            win_rate_1d = float((valid_1d > 0).mean())
            avg_return_1d = float(valid_1d.mean())

    # 1w 지표
    col_1w = "outcome_1w"
    win_rate_1w: float | None = None
    avg_return_1w: float | None = None
    if col_1w in outcomes_df.columns:
        valid_1w = outcomes_df[col_1w].dropna()
        if len(valid_1w) > 0:
            win_rate_1w = float((valid_1w > 0).mean())
            avg_return_1w = float(valid_1w.mean())

    return DashboardMetrics(
        total_signals=total,
        win_rate_1d=win_rate_1d,
        win_rate_1w=win_rate_1w,
        avg_return_1d=avg_return_1d,
        avg_return_1w=avg_return_1w,
    )


def compute_strategy_summary(outcomes_df: pd.DataFrame) -> pd.DataFrame:
    """전략별 집계 DataFrame 반환.

    Parameters
    ----------
    outcomes_df : pd.DataFrame
        결과 데이터 (strategy_name, outcome_1d 컬럼 포함)

    Returns
    -------
    pd.DataFrame
        컬럼: strategy_name, signal_count, win_rate_1d, avg_return_1d
        빈 outcomes_df이면 빈 DataFrame 반환.

    Notes
    -----
    outcome_1d 컬럼이 없거나 전부 NaN이면 win_rate_1d / avg_return_1d는 NaN.
    """
    if outcomes_df.empty or "strategy_name" not in outcomes_df.columns:
        return pd.DataFrame()

    # outcome_1d 컬럼 없으면 NaN 컬럼 추가
    if "outcome_1d" not in outcomes_df.columns:
        outcomes_df = outcomes_df.copy()
        outcomes_df["outcome_1d"] = float("nan")

    summary = (
        outcomes_df.groupby("strategy_name")
        .agg(
            signal_count=("strategy_name", "count"),
            win_rate_1d=(
                "outcome_1d",
                lambda s: (
                    float((s.dropna() > 0).mean())
                    if s.dropna().empty is False
                    else float("nan")
                ),
            ),
            avg_return_1d=(
                "outcome_1d",
                lambda s: (
                    float(s.dropna().mean())
                    if s.dropna().empty is False
                    else float("nan")
                ),
            ),
        )
        .reset_index()
    )
    return summary
