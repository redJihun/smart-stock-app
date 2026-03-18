"""백테스팅 엔진 모듈 테스트."""

from __future__ import annotations

import math
from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.backtesting.engine import BacktestEngine, BacktestResult


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


class TestBacktestEngineInit:
    """BacktestEngine 초기화 테스트."""

    def test_default_initial_capital(self) -> None:
        """기본 초기 자본금은 1,000,000."""
        engine = BacktestEngine()
        assert engine.initial_capital == 1_000_000.0

    def test_invalid_capital_raises(self) -> None:
        """초기 자본금이 0 이하면 ValueError 발생."""
        with pytest.raises(ValueError, match="initial_capital은 0보다 커야"):
            BacktestEngine(initial_capital=0)

        with pytest.raises(ValueError, match="initial_capital은 0보다 커야"):
            BacktestEngine(initial_capital=-1000)


class TestBacktestEngineRun:
    """BacktestEngine.run() 테스트."""

    def test_returns_backtest_result_type(self) -> None:
        """반환 타입이 BacktestResult."""
        engine = BacktestEngine()
        df = _make_sample_df()

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [0] * len(df),
            index=df.index,
        )

        result = engine.run(df, strategy)
        assert isinstance(result, BacktestResult)

    def test_portfolio_length_matches_input(self) -> None:
        """포트폴리오 길이가 입력 데이터 길이와 일치."""
        engine = BacktestEngine()
        df = _make_sample_df(rows=60)

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [0] * len(df),
            index=df.index,
        )

        result = engine.run(df, strategy)
        assert len(result.portfolio) == len(df)

    def test_portfolio_index_matches_input(self) -> None:
        """포트폴리오 인덱스가 입력 데이터 인덱스와 일치."""
        engine = BacktestEngine()
        df = _make_sample_df(rows=60)

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [0] * len(df),
            index=df.index,
        )

        result = engine.run(df, strategy)
        assert (result.portfolio.index == df.index).all()

    def test_always_hold_zero_pnl(self) -> None:
        """모든 신호가 0(보유 안 함)이면 포트폴리오 변동 없음."""
        engine = BacktestEngine(initial_capital=1_000_000)
        df = _make_sample_df(rows=60)

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [0] * len(df),
            index=df.index,
        )

        result = engine.run(df, strategy)
        # 포트폴리오는 초기 자본금을 유지해야 함
        assert result.portfolio.iloc[0] == pytest.approx(1_000_000.0)
        assert result.portfolio.iloc[-1] == pytest.approx(1_000_000.0)

    def test_trade_count_single_cycle(self) -> None:
        """단일 매수→매도 사이클 거래 수는 1."""
        engine = BacktestEngine()
        df = _make_sample_df(rows=60)

        # 처음 10일은 0, 10~40일은 1, 이후 0
        signals = [0] * 10 + [1] * 30 + [0] * 20
        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            signals,
            index=df.index,
        )

        result = engine.run(df, strategy)
        assert result.trade_count == 1

    def test_win_rate_nan_when_no_trade(self) -> None:
        """거래가 없으면 win_rate는 NaN."""
        engine = BacktestEngine()
        df = _make_sample_df(rows=60)

        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [0] * len(df),
            index=df.index,
        )

        result = engine.run(df, strategy)
        assert math.isnan(result.win_rate)
