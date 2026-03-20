"""거래 비용 모델 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.backtesting.cost_model import TradingCost
from smart_stock.backtesting.engine import BacktestEngine


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


class TestTradingCostInit:
    """TradingCost 초기화 테스트."""

    def test_default_values(self) -> None:
        """기본값은 한국 주식 기준."""
        cost = TradingCost()
        assert cost.commission_rate == pytest.approx(0.00015)
        assert cost.tax_rate == pytest.approx(0.0018)
        assert cost.slippage_rate == pytest.approx(0.0005)

    def test_custom_values(self) -> None:
        """커스텀 값 설정 확인."""
        cost = TradingCost(
            commission_rate=0.0001,
            tax_rate=0.001,
            slippage_rate=0.0002,
        )
        assert cost.commission_rate == pytest.approx(0.0001)
        assert cost.tax_rate == pytest.approx(0.001)
        assert cost.slippage_rate == pytest.approx(0.0002)

    def test_negative_commission_raises(self) -> None:
        """commission_rate < 0 → ValueError."""
        with pytest.raises(ValueError, match="commission_rate은 0 이상이어야"):
            TradingCost(commission_rate=-0.0001)

    def test_negative_tax_raises(self) -> None:
        """tax_rate < 0 → ValueError."""
        with pytest.raises(ValueError, match="tax_rate은 0 이상이어야"):
            TradingCost(tax_rate=-0.001)

    def test_negative_slippage_raises(self) -> None:
        """slippage_rate < 0 → ValueError."""
        with pytest.raises(ValueError, match="slippage_rate은 0 이상이어야"):
            TradingCost(slippage_rate=-0.0001)

    def test_zero_rates_valid(self) -> None:
        """모든 비율 0은 정상 초기화."""
        cost = TradingCost(commission_rate=0, tax_rate=0, slippage_rate=0)
        assert cost.commission_rate == 0
        assert cost.tax_rate == 0
        assert cost.slippage_rate == 0


class TestTradingCostRates:
    """TradingCost 비용율 계산 테스트."""

    def test_buy_cost_rate(self) -> None:
        """매수 시 비용율 = commission + slippage."""
        cost = TradingCost(
            commission_rate=0.0001,
            tax_rate=0.001,
            slippage_rate=0.0002,
        )
        assert cost.buy_cost_rate() == pytest.approx(0.0003)

    def test_sell_cost_rate(self) -> None:
        """매도 시 비용율 = commission + tax + slippage."""
        cost = TradingCost(
            commission_rate=0.0001,
            tax_rate=0.001,
            slippage_rate=0.0002,
        )
        assert cost.sell_cost_rate() == pytest.approx(0.0013)


class TestBacktestEngineWithCost:
    """비용 모델이 적용된 BacktestEngine 테스트."""

    def test_cost_model_none_same_as_no_cost(self) -> None:
        """cost_model=None 시 기존 포트폴리오와 동일."""
        df = _make_sample_df()
        signals = pd.Series([0] * 30 + [1] * 30, index=df.index)

        strategy = MagicMock()
        strategy.generate_signals.return_value = signals

        engine_no_cost = BacktestEngine(initial_capital=1_000_000)
        engine_with_none = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=None,
        )

        result_no_cost = engine_no_cost.run(df, strategy)
        result_with_none = engine_with_none.run(df, strategy)

        assert (result_no_cost.portfolio == result_with_none.portfolio).all()
        assert result_no_cost.total_cost == result_with_none.total_cost == 0.0

    def test_cost_applied_reduces_portfolio(self) -> None:
        """cost_model 적용 시 포트폴리오 < 미적용."""
        df = _make_sample_df()
        signals = pd.Series([0] * 30 + [1] * 30, index=df.index)

        strategy = MagicMock()
        strategy.generate_signals.return_value = signals

        engine_no_cost = BacktestEngine(initial_capital=1_000_000)
        engine_with_cost = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=TradingCost(),
        )

        result_no_cost = engine_no_cost.run(df, strategy)
        result_with_cost = engine_with_cost.run(df, strategy)

        # 비용 적용 시 최종 포트폴리오 값이 작아야 함
        assert result_with_cost.portfolio.iloc[-1] < result_no_cost.portfolio.iloc[-1]
        assert result_with_cost.total_cost > 0.0

    def test_zero_cost_equals_no_cost(self) -> None:
        """모든 비율 0인 TradingCost → cost_model=None과 동일."""
        df = _make_sample_df()
        signals = pd.Series([0] * 30 + [1] * 30, index=df.index)

        strategy = MagicMock()
        strategy.generate_signals.return_value = signals

        engine_no_cost = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=None,
        )
        engine_zero_cost = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=TradingCost(
                commission_rate=0,
                tax_rate=0,
                slippage_rate=0,
            ),
        )

        result_no_cost = engine_no_cost.run(df, strategy)
        result_zero_cost = engine_zero_cost.run(df, strategy)

        assert (result_no_cost.portfolio == result_zero_cost.portfolio).all()
        assert result_zero_cost.total_cost == pytest.approx(0.0)

    def test_total_cost_positive_with_trades(self) -> None:
        """거래 있으면 total_cost > 0."""
        df = _make_sample_df()
        # 3개 사이클: (0-10=0, 10-20=1, 20-30=0, 30-40=1, 40-50=0, 50-60=1)
        signals = pd.Series(
            [0] * 10 + [1] * 10 + [0] * 10 + [1] * 10 + [0] * 10 + [1] * 10,
            index=df.index,
        )

        strategy = MagicMock()
        strategy.generate_signals.return_value = signals

        engine = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=TradingCost(),
        )
        result = engine.run(df, strategy)

        assert result.total_cost > 0.0
        assert result.trade_count > 0

    def test_total_cost_zero_without_trades(self) -> None:
        """거래 없으면 total_cost == 0.0."""
        df = _make_sample_df()
        signals = pd.Series([0] * len(df), index=df.index)

        strategy = MagicMock()
        strategy.generate_signals.return_value = signals

        engine = BacktestEngine(
            initial_capital=1_000_000,
            cost_model=TradingCost(),
        )
        result = engine.run(df, strategy)

        assert result.total_cost == pytest.approx(0.0)
        assert result.trade_count == 0
