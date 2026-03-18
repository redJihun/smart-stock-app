"""run_and_track 파이프라인 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from smart_stock.backtesting.engine import BacktestEngine, BacktestResult
from smart_stock.backtesting.pipeline import run_and_track
from smart_stock.tracking.logger import SignalLogger


def _make_df(n: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV DataFrame."""
    idx = pd.date_range("2024-01-02", periods=n, freq="B")
    prices = [100.0 + i for i in range(n)]
    return pd.DataFrame(
        {
            "Open": prices,
            "High": [p + 1 for p in prices],
            "Low": [p - 1 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=idx,
    )


def _make_strategy_mock(signals: pd.Series) -> MagicMock:
    strategy = MagicMock()
    strategy.generate_signals.return_value = signals
    return strategy


class TestRunAndTrackReturn:
    def test_returns_backtest_result(self, tmp_path: Path) -> None:
        """반환값이 BacktestResult 인스턴스여야 함."""
        df = _make_df()
        # 항상 0 시그널 (변화 없음)
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        result = run_and_track(df, strategy, ticker="005930", logger=logger)
        assert isinstance(result, BacktestResult)

    def test_engine_default_created(self, tmp_path: Path) -> None:
        """engine=None 이면 기본 BacktestEngine이 사용됨."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        # engine 파라미터 없이 호출 — 에러 없음
        result = run_and_track(df, strategy, ticker="005930", logger=logger)
        assert result.total_return is not None


class TestRunAndTrackSignalLogging:
    def test_no_signals_logged_when_all_zero(self, tmp_path: Path) -> None:
        """항상 0 시그널이면 기록 없음."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        assert logger.load().empty

    def test_buy_signal_logged(self, tmp_path: Path) -> None:
        """0→1 변화 시점에서 signal=1 레코드가 기록됨."""
        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        logged = logger.load()
        assert len(logged) == 1
        assert int(logged.iloc[0]["signal"]) == 1

    def test_sell_signal_logged(self, tmp_path: Path) -> None:
        """1→0 변화 시점에서 signal=-1 레코드가 기록됨."""
        df = _make_df(n=20)
        vals = [1] * 10 + [0] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        logged = logger.load()
        assert len(logged) == 1
        assert int(logged.iloc[0]["signal"]) == -1

    def test_strategy_name_recorded(self, tmp_path: Path) -> None:
        """strategy_name이 클래스명으로 기록됨."""
        from smart_stock.strategies.base_strategy import BaseStrategy

        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)

        class DummyStrategy(BaseStrategy):  # type: ignore[misc]
            @property
            def name(self) -> str:
                return "dummy"

            def generate_signals(self, df: pd.DataFrame) -> pd.Series:
                return signals

        strategy = DummyStrategy()
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="035720", logger=logger)
        logged = logger.load()
        assert logged.iloc[0]["strategy_name"] == "DummyStrategy"

    def test_ticker_recorded(self, tmp_path: Path) -> None:
        """ticker가 기록에 저장됨."""
        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="AAPL", logger=logger)
        logged = logger.load()
        assert logged.iloc[0]["ticker"] == "AAPL"

    def test_custom_engine_used(self, tmp_path: Path) -> None:
        """주입된 engine이 실제로 사용됨."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        custom_engine = BacktestEngine(initial_capital=500_000)
        result = run_and_track(
            df, strategy, ticker="005930", engine=custom_engine, logger=logger
        )
        assert isinstance(result, BacktestResult)
