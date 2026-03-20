"""포지션 사이징 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.backtesting.engine import BacktestEngine
from smart_stock.backtesting.position_sizer import (
    FixedAmountSizer,
    FixedFractionSizer,
    KellyCriterionSizer,
)


def _make_sample_df(rows: int = 60) -> pd.DataFrame:
    """샘플 OHLCV 데이터프레임을 생성합니다.

    Parameters
    ----------
    rows : int, optional
        행 수 (기본값: 60)

    Returns
    -------
    pd.DataFrame
        샘플 OHLCV 데이터
    """
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    close = [100.0 + i for i in range(rows)]
    return pd.DataFrame(
        {
            "Open": [p - 1 for p in close],
            "High": [p + 2 for p in close],
            "Low": [p - 2 for p in close],
            "Close": close,
            "Volume": [1_000_000] * rows,
        },
        index=idx,
    )


class TestFixedAmountSizer:
    """고정 금액 사이저 테스트."""

    def test_normal_fraction_calculation(self) -> None:
        """정상 케이스: amount=500_000, portfolio=1_000_000 → 0.5."""
        sizer = FixedAmountSizer(amount=500_000)
        fraction = sizer.calculate(portfolio_value=1_000_000, trade_returns=[])
        assert fraction == 0.5

    def test_clips_to_one_when_amount_exceeds_portfolio(self) -> None:
        """amount > portfolio → 1.0으로 클리핑."""
        sizer = FixedAmountSizer(amount=2_000_000)
        fraction = sizer.calculate(portfolio_value=1_000_000, trade_returns=[])
        assert fraction == 1.0

    def test_invalid_amount_raises(self) -> None:
        """amount <= 0 → ValueError."""
        with pytest.raises(ValueError, match="amount는 0보다 커야 합니다"):
            FixedAmountSizer(amount=0)
        with pytest.raises(ValueError, match="amount는 0보다 커야 합니다"):
            FixedAmountSizer(amount=-100)

    def test_ignores_trade_returns(self) -> None:
        """trade_returns에 무관하게 동일 결과."""
        sizer = FixedAmountSizer(amount=100_000)
        f1 = sizer.calculate(1_000_000, [])
        f2 = sizer.calculate(1_000_000, [0.05, -0.02, 0.1])
        assert f1 == f2 == 0.1


class TestFixedFractionSizer:
    """고정 비율 사이저 테스트."""

    def test_returns_fixed_fraction(self) -> None:
        """항상 고정된 비율 반환."""
        sizer = FixedFractionSizer(fraction=0.3)
        f1 = sizer.calculate(1_000_000, [])
        f2 = sizer.calculate(500_000, [0.05, -0.02])
        assert f1 == f2 == 0.3

    def test_full_capital_valid(self) -> None:
        """fraction=1.0 허용."""
        sizer = FixedFractionSizer(fraction=1.0)
        fraction = sizer.calculate(1_000_000, [])
        assert fraction == 1.0

    def test_zero_fraction_raises(self) -> None:
        """fraction=0.0 → ValueError."""
        with pytest.raises(ValueError, match="fraction은 \\(0, 1\\] 범위여야 합니다"):
            FixedFractionSizer(fraction=0.0)

    def test_over_one_raises(self) -> None:
        """fraction > 1.0 → ValueError."""
        with pytest.raises(ValueError, match="fraction은 \\(0, 1\\] 범위여야 합니다"):
            FixedFractionSizer(fraction=1.1)


class TestKellyCriterionSizer:
    """Kelly Criterion 사이저 테스트."""

    def test_no_trades_returns_zero(self) -> None:
        """[] → 0.0."""
        sizer = KellyCriterionSizer()
        fraction = sizer.calculate(1_000_000, [])
        assert fraction == 0.0

    def test_one_trade_returns_zero(self) -> None:
        """[0.1] (1개) → 0.0 (통계적 불충분)."""
        sizer = KellyCriterionSizer()
        fraction = sizer.calculate(1_000_000, [0.1])
        assert fraction == 0.0

    def test_only_wins_returns_max_fraction(self) -> None:
        """손실 없음 → max_fraction."""
        sizer = KellyCriterionSizer(max_fraction=0.25)
        fraction = sizer.calculate(1_000_000, [0.05, 0.1, 0.02])
        assert fraction == 0.25

    def test_only_losses_returns_zero(self) -> None:
        """이익 없음 → 0.0."""
        sizer = KellyCriterionSizer()
        fraction = sizer.calculate(1_000_000, [-0.05, -0.1, -0.02])
        assert fraction == 0.0

    def test_negative_f_star_clips_to_zero(self) -> None:
        """기대값 음수 전략 → 0.0."""
        sizer = KellyCriterionSizer()
        returns = [0.01, 0.01, -0.2]
        fraction = sizer.calculate(1_000_000, returns)
        assert fraction == 0.0

    def test_exceeds_max_fraction_clips(self) -> None:
        """f* > max_fraction → max_fraction으로 클리핑."""
        sizer = KellyCriterionSizer(max_fraction=0.1)
        returns = [0.1, 0.1, 0.1, -0.05]
        fraction = sizer.calculate(1_000_000, returns)
        assert fraction == 0.1

    def test_invalid_max_fraction_raises(self) -> None:
        """max_fraction <= 0 또는 > 1.0 → ValueError."""
        with pytest.raises(ValueError, match="max_fraction은 \\(0, 1\\] 범위여야 합니다"):
            KellyCriterionSizer(max_fraction=0)
        with pytest.raises(ValueError, match="max_fraction은 \\(0, 1\\] 범위여야 합니다"):
            KellyCriterionSizer(max_fraction=1.5)


class TestPositionSizerIntegration:
    """PositionSizer와 BacktestEngine 통합 테스트."""

    def test_engine_with_fixed_fraction_sizer_reduces_portfolio(self) -> None:
        """FixedFractionSizer(0.5) 적용 시 100% 투입 대비 변동 확인."""
        df = _make_sample_df(rows=100)
        signals = [0] * 20 + [1] * 60 + [0] * 20

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            signals,
            index=df.index,
        )

        engine_full = BacktestEngine(initial_capital=1_000_000)
        result_full = engine_full.run(df, strategy)

        engine_half = BacktestEngine(
            initial_capital=1_000_000,
            position_sizer=FixedFractionSizer(0.5),
        )
        result_half = engine_half.run(df, strategy)

        assert result_full.total_return > result_half.total_return

    def test_engine_none_sizer_backward_compatible(self) -> None:
        """position_sizer=None → 기존 동작과 동일."""
        df = _make_sample_df(rows=100)
        signals = [0] * 20 + [1] * 60 + [0] * 20

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            signals,
            index=df.index,
        )

        engine_none = BacktestEngine(initial_capital=1_000_000)
        result_none = engine_none.run(df, strategy)

        engine_explicit = BacktestEngine(
            initial_capital=1_000_000,
            position_sizer=None,
        )
        result_explicit = engine_explicit.run(df, strategy)

        assert result_none.total_return == result_explicit.total_return
        assert (result_none.portfolio == result_explicit.portfolio).all()
