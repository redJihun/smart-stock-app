"""대시보드 데이터 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from smart_stock.dashboard.data import (
    DashboardMetrics,
    compute_metrics,
    compute_strategy_summary,
    load_outcomes,
    load_signals,
)


def _make_signals_df() -> pd.DataFrame:
    """테스트용 시그널 DataFrame 생성."""
    return pd.DataFrame({
        "strategy_name": ["SMA", "SMA"],
        "ticker": ["005930", "005930"],
        "signal_date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "signal": [1, -1],
        "price": [70000.0, 72000.0],
        "logged_at": pd.to_datetime(["2024-01-02", "2024-01-03"]),
    })


def _make_outcomes_df(
    outcome_1d: list[float | None] | None = None,
    outcome_1w: list[float | None] | None = None,
) -> pd.DataFrame:
    """테스트용 결과 DataFrame 생성."""
    n = 3
    o1d = outcome_1d if outcome_1d is not None else [0.01, -0.005, 0.02]
    o1w = outcome_1w if outcome_1w is not None else [0.02, -0.01, 0.03]
    return pd.DataFrame({
        "strategy_name": ["SMA", "SMA", "RSI"],
        "ticker": ["005930", "005930", "035720"],
        "signal_date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
        "signal": [1, 1, 1],
        "entry_price": [70000.0, 71000.0, 50000.0],
        "outcome_1d": o1d,
        "outcome_1w": o1w,
        "updated_at": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
    })


class TestLoadSignals:
    """load_signals 함수 테스트."""

    def test_load_signals_missing_file(self, tmp_path: Path) -> None:
        """파일 없으면 빈 DataFrame 반환."""
        result = load_signals(tmp_path)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_load_signals_returns_dataframe(self, tmp_path: Path) -> None:
        """signals.parquet 파일 로드."""
        signals_df = _make_signals_df()
        signals_df.to_parquet(tmp_path / "signals.parquet")

        result = load_signals(tmp_path)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == [
            "strategy_name",
            "ticker",
            "signal_date",
            "signal",
            "price",
            "logged_at",
        ]


class TestLoadOutcomes:
    """load_outcomes 함수 테스트."""

    def test_load_outcomes_missing_file(self, tmp_path: Path) -> None:
        """파일 없으면 빈 DataFrame 반환."""
        result = load_outcomes(tmp_path)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_load_outcomes_returns_dataframe(self, tmp_path: Path) -> None:
        """outcomes.parquet 파일 로드."""
        outcomes_df = _make_outcomes_df()
        outcomes_df.to_parquet(tmp_path / "outcomes.parquet")

        result = load_outcomes(tmp_path)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "outcome_1d" in result.columns
        assert "outcome_1w" in result.columns


class TestComputeMetrics:
    """compute_metrics 함수 테스트."""

    def test_metrics_empty_df(self) -> None:
        """빈 DataFrame → DashboardMetrics(total_signals=0, 나머지 None)."""
        empty_df = pd.DataFrame()
        metrics = compute_metrics(empty_df)

        assert isinstance(metrics, DashboardMetrics)
        assert metrics.total_signals == 0
        assert metrics.win_rate_1d is None
        assert metrics.win_rate_1w is None
        assert metrics.avg_return_1d is None
        assert metrics.avg_return_1w is None

    def test_metrics_win_rate_1d(self) -> None:
        """outcome_1d > 0인 비율 계산."""
        outcomes_df = _make_outcomes_df(outcome_1d=[0.01, -0.005, 0.02])
        metrics = compute_metrics(outcomes_df)

        assert metrics.total_signals == 3
        # 2/3 = 0.6666...
        assert abs(metrics.win_rate_1d - (2 / 3)) < 0.001 if metrics.win_rate_1d is not None else False

    def test_metrics_avg_return_1d(self) -> None:
        """평균 수익률 계산."""
        outcomes_df = _make_outcomes_df(outcome_1d=[0.01, -0.005, 0.02])
        metrics = compute_metrics(outcomes_df)

        expected_avg = (0.01 - 0.005 + 0.02) / 3
        assert abs(metrics.avg_return_1d - expected_avg) < 0.001 if metrics.avg_return_1d is not None else False

    def test_metrics_no_1d_data(self) -> None:
        """outcome_1d 컬럼 없으면 win_rate_1d/avg_return_1d는 None."""
        outcomes_df = pd.DataFrame({
            "strategy_name": ["SMA"],
            "ticker": ["005930"],
            "signal_date": pd.to_datetime(["2024-01-02"]),
            "signal": [1],
        })
        metrics = compute_metrics(outcomes_df)

        assert metrics.total_signals == 1
        assert metrics.win_rate_1d is None
        assert metrics.avg_return_1d is None


class TestComputeStrategySummary:
    """compute_strategy_summary 함수 테스트."""

    def test_summary_empty_df(self) -> None:
        """빈 DataFrame → 빈 DataFrame."""
        empty_df = pd.DataFrame()
        summary = compute_strategy_summary(empty_df)
        assert summary.empty

    def test_summary_groups_by_strategy(self) -> None:
        """전략별 집계 및 신호 개수 검증."""
        outcomes_df = _make_outcomes_df()
        summary = compute_strategy_summary(outcomes_df)

        assert len(summary) == 2
        assert set(summary["strategy_name"]) == {"SMA", "RSI"}

        sma_row = summary[summary["strategy_name"] == "SMA"].iloc[0]
        assert sma_row["signal_count"] == 2

        rsi_row = summary[summary["strategy_name"] == "RSI"].iloc[0]
        assert rsi_row["signal_count"] == 1
