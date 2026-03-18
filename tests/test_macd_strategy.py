from __future__ import annotations

import pandas as pd
import pytest

from smart_stock.strategies.macd_strategy import MACDStrategy


def _make_sample_df(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV 샘플 DataFrame을 생성한다.

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60, MACD 계산에 충분함)

    Returns
    -------
    pd.DataFrame
        OHLCV 데이터를 포함하는 DataFrame
    """
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    return pd.DataFrame(
        {
            "Open": [70000.0] * rows,
            "High": [71000.0] * rows,
            "Low": [69000.0] * rows,
            "Close": [70500.0] * rows,
            "Volume": [1_000_000] * rows,
        },
        index=idx,
    )


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """기본 샘플 DataFrame fixture."""
    return _make_sample_df(rows=60)


@pytest.fixture()
def macd_strategy() -> MACDStrategy:
    """기본값으로 초기화한 MACDStrategy fixture."""
    return MACDStrategy()


class TestMACDStrategyInit:
    """초기화 관련 테스트."""

    def test_fast_gte_slow_raises(self) -> None:
        """fast_period >= slow_period인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="fast_period"):
            MACDStrategy(fast_period=26, slow_period=26)

        with pytest.raises(ValueError, match="fast_period"):
            MACDStrategy(fast_period=30, slow_period=26)

    def test_invalid_signal_period_raises(self) -> None:
        """signal_period < 1인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="signal_period"):
            MACDStrategy(signal_period=0)


class TestMACDStrategyName:
    """name 프로퍼티 관련 테스트."""

    def test_name_format_default(self) -> None:
        """기본값으로 초기화한 전략의 name이 올바른 형식인지 확인."""
        strategy = MACDStrategy()
        assert strategy.name == "MACD_12_26_9"

    def test_name_format_custom(self) -> None:
        """커스텀 주기 값으로 초기화한 전략의 name 확인."""
        strategy = MACDStrategy(fast_period=10, slow_period=20, signal_period=5)
        assert strategy.name == "MACD_10_20_5"


class TestMACDStrategySignals:
    """generate_signals 메서드 관련 테스트."""

    def test_generate_signals_returns_series(self, sample_df: pd.DataFrame) -> None:
        """반환값이 pd.Series인지 확인."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_df)
        assert isinstance(signals, pd.Series)

    def test_signals_are_binary(self, sample_df: pd.DataFrame) -> None:
        """신호 값이 0 또는 1만 포함하는지 확인."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_df)
        unique_values = set(signals.unique())
        assert unique_values.issubset({0, 1})

    def test_signals_length_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 길이가 입력 DataFrame과 동일한지 확인."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_df)
        assert len(signals) == len(sample_df)

    def test_signals_index_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 인덱스가 입력 DataFrame과 동일한지 확인."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_df)
        pd.testing.assert_index_equal(signals.index, sample_df.index)

    def test_no_nan_in_signals(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈에 NaN이 없는지 확인."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_df)
        assert not signals.isna().any()
