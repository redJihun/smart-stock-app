"""페이퍼 트레이딩 실행기 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.backtesting.cost_model import TradingCost
from smart_stock.backtesting.position_sizer import PositionSizer
from smart_stock.data.feed import DataFeed
from smart_stock.strategies.base_strategy import BaseStrategy
from smart_stock.tracking.logger import SignalLogger
from smart_stock.trading.paper_trader import PaperTrader


def _make_sample_df(
    start: str = "2024-01-02 09:30",
    periods: int = 1,
    close_prices: list[float] | None = None,
) -> pd.DataFrame:
    """테스트용 샘플 데이터프레임 생성.

    Parameters
    ----------
    start : str
        시작 시간 (기본값: "2024-01-02 09:30")
    periods : int
        캔들 개수 (기본값: 1)
    close_prices : list[float] | None
        종가 리스트 (기본값: None → [100.0] * periods)

    Returns
    -------
    pd.DataFrame
        OHLCV 데이터
    """
    idx = pd.date_range(start, periods=periods, freq="5min")
    closes = close_prices if close_prices is not None else [100.0] * periods
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [p + 1.0 for p in closes],
            "Low": [p - 1.0 for p in closes],
            "Close": closes,
            "Volume": [10_000] * periods,
        },
        index=idx,
    )


def _make_mock_strategy(signals: list[int]) -> BaseStrategy:
    """mock BaseStrategy 생성.

    Parameters
    ----------
    signals : list[int]
        신호 시퀀스

    Returns
    -------
    BaseStrategy
        generate_signals가 hist 길이에 맞춘 Series를 반환하는 mock
    """
    strategy = MagicMock(spec=BaseStrategy)
    strategy.name = "MockStrategy"

    def _gen(df: pd.DataFrame) -> pd.Series:
        n = len(df)
        padded = signals + [signals[-1]] * max(0, n - len(signals))
        return pd.Series(padded[:n], index=df.index, dtype=float)

    strategy.generate_signals.side_effect = _gen
    return strategy


def _make_mock_feed() -> DataFeed:
    """mock DataFeed 생성.

    Returns
    -------
    DataFeed
        mock feed
    """
    return MagicMock(spec=DataFeed)


class TestPaperTraderInit:
    """초기화 관련 테스트."""

    def test_initial_portfolio_value_equals_capital(self) -> None:
        """portfolio_value는 초기에 initial_capital과 같아야 한다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=1_000_000.0)
        assert trader.portfolio_value == 1_000_000.0

    def test_initial_position_is_zero(self) -> None:
        """초기 position은 0이어야 한다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930")
        assert trader.position == 0

    def test_invalid_capital_raises(self) -> None:
        """initial_capital <= 0이면 ValueError를 raise한다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        with pytest.raises(ValueError, match="initial_capital은 0보다 커야"):
            PaperTrader(strategy, feed, "005930", initial_capital=0)


class TestPaperTraderBuy:
    """매수 관련 테스트."""

    def test_buy_increases_shares(self) -> None:
        """매수 후 _shares > 0이어야 한다."""
        strategy = _make_mock_strategy([0, 1])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=100_000.0)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)  # history=[09:30], signal=0
        assert trader._shares == 0.0

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)  # history=[09:30, 09:35], signal=1 (0→1 전환)
        assert trader._shares > 0.0

    def test_buy_decreases_cash(self) -> None:
        """매수 후 _cash < initial_capital이어야 한다."""
        strategy = _make_mock_strategy([0, 1])
        feed = _make_mock_feed()
        initial = 100_000.0
        trader = PaperTrader(strategy, feed, "005930", initial_capital=initial)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)
        assert trader._cash < initial

    def test_buy_with_cost_model(self) -> None:
        """cost_model이 있으면 비용이 차감되어야 한다."""
        strategy = _make_mock_strategy([0, 1])
        feed = _make_mock_feed()
        cost = TradingCost(commission_rate=0.001, tax_rate=0.0, slippage_rate=0.0)
        trader = PaperTrader(
            strategy, feed, "005930", initial_capital=100_000.0, cost_model=cost
        )

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)

        # invest = 100_000.0, price = 100.0, buy_cost_rate = 0.001
        # shares = 100_000.0 / (100.0 * 1.001) ≈ 999.001
        expected_shares = 100_000.0 / (100.0 * 1.001)
        assert abs(trader._shares - expected_shares) < 0.01


class TestPaperTraderSell:
    """매도 관련 테스트."""

    def test_sell_clears_shares(self) -> None:
        """매도 후 _shares == 0이어야 한다."""
        strategy = _make_mock_strategy([0, 1, 0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=100_000.0)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)  # history=[09:30], signal=0

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)  # history=[09:30, 09:35], signal=1 (0→1 전환, 매수)
        assert trader._shares > 0.0

        df3 = _make_sample_df(start="2024-01-02 09:40", periods=1, close_prices=[100.0])
        trader._on_candle(df3)  # history=[09:30, 09:35, 09:40], signal=0 (1→0 전환, 매도)
        assert trader._shares == 0.0

    def test_sell_records_trade_return(self) -> None:
        """매도 후 trade_return이 기록되어야 한다."""
        strategy = _make_mock_strategy([0, 1, 0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=100_000.0)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)  # 매수 @ 100

        df3 = _make_sample_df(start="2024-01-02 09:40", periods=1, close_prices=[110.0])
        trader._on_candle(df3)  # 매도 @ 110
        # trade_return = 110 / 100 - 1 = 0.1
        assert len(trader._completed_trade_returns) == 1
        assert abs(trader._completed_trade_returns[0] - 0.1) < 0.001

    def test_sell_with_cost_model(self) -> None:
        """cost_model이 있으면 매도액에서 비용이 차감되어야 한다."""
        strategy = _make_mock_strategy([0, 1, 0])
        feed = _make_mock_feed()
        cost = TradingCost(commission_rate=0.001, tax_rate=0.001, slippage_rate=0.0)
        trader = PaperTrader(
            strategy, feed, "005930", initial_capital=100_000.0, cost_model=cost
        )

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)  # 매수
        # shares = 100_000 / (100 * 1.001), cash = 0

        cash_after_buy = trader._cash
        shares_at_entry = trader._shares
        df3 = _make_sample_df(start="2024-01-02 09:40", periods=1, close_prices=[100.0])
        trader._on_candle(df3)  # 매도

        # proceeds = shares_at_entry * 100
        # net = proceeds * (1 - 0.002)
        proceeds = shares_at_entry * 100.0
        expected_net = proceeds * (1.0 - 0.002)
        assert trader._cash > cash_after_buy
        assert abs(trader._cash - (cash_after_buy + expected_net)) < 0.01


class TestPaperTraderSignalFlow:
    """신호 흐름 관련 테스트."""

    def test_no_signal_change_no_action(self) -> None:
        """신호 변화가 없으면 매수/매도가 발생하지 않는다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=100_000.0)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)
        assert trader._shares == 0.0
        assert trader._cash == 100_000.0

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)
        assert trader._shares == 0.0
        assert trader._cash == 100_000.0

    def test_buy_then_sell_portfolio_value(self) -> None:
        """매수 → 매도 후 손익이 반영되어야 한다."""
        strategy = _make_mock_strategy([0, 1, 0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930", initial_capital=100_000.0)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=1, close_prices=[100.0])
        trader._on_candle(df2)  # 매수 @ 100

        df3 = _make_sample_df(start="2024-01-02 09:40", periods=1, close_prices=[110.0])
        trader._on_candle(df3)  # 매도 @ 110
        # 10% 수익
        assert trader.portfolio_value > 100_000.0

    def test_logger_called_on_signal(self) -> None:
        """신호 변화 시 logger가 호출되어야 한다."""
        strategy = _make_mock_strategy([0, 1])
        feed = _make_mock_feed()
        logger = MagicMock(spec=SignalLogger)
        trader = PaperTrader(strategy, feed, "005930", logger=logger)

        df1 = _make_sample_df(periods=1, close_prices=[100.0])
        trader._on_candle(df1)  # signal=0, prev=0 → no change

        df2 = _make_sample_df(start="2024-01-02 09:35", periods=2, close_prices=[100.0, 100.0])
        trader._on_candle(df2)  # signal=1, prev=0 → change
        logger.log.assert_called_once()


class TestPaperTraderLifecycle:
    """생명주기 관련 테스트."""

    def test_start_stop_no_error(self) -> None:
        """start/stop이 오류 없이 동작한다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930")

        trader.start()
        feed.subscribe.assert_called_once()
        feed.start.assert_called_once()

        trader.stop()
        feed.stop.assert_called_once()

    def test_context_manager(self) -> None:
        """with 블록 탈출 후 feed.stop이 호출된다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930")

        with trader:
            pass

        feed.start.assert_called_once()
        feed.stop.assert_called_once()

    def test_double_start_no_error(self) -> None:
        """start() 2번 호출 시 feed.subscribe는 1회만 호출된다."""
        strategy = _make_mock_strategy([0])
        feed = _make_mock_feed()
        trader = PaperTrader(strategy, feed, "005930")

        trader.start()
        trader.start()

        feed.subscribe.assert_called_once()
