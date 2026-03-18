from __future__ import annotations

import pandas as pd
import pytest

from smart_stock.strategies.rsi_strategy import RSIStrategy


def _make_sample_df(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV 샘플 DataFrame을 생성한다.

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60, RSI 계산에 충분함)

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
    return _make_sample_df()


@pytest.fixture()
def sample_df_short() -> pd.DataFrame:
    """짧은 시계열 fixture (엣지케이스용)."""
    return _make_sample_df(rows=5)


@pytest.fixture()
def rsi_strategy() -> RSIStrategy:
    """기본값으로 초기화한 RSI 전략 fixture."""
    return RSIStrategy()


class TestRSIStrategyInit:
    """초기화 관련 테스트."""

    def test_invalid_period_raises(self) -> None:
        """period < 1인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="period"):
            RSIStrategy(period=0)

        with pytest.raises(ValueError, match="period"):
            RSIStrategy(period=-1)

    def test_invalid_oversold_overbought(self) -> None:
        """oversold >= overbought인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="oversold"):
            RSIStrategy(oversold=70.0, overbought=70.0)

        with pytest.raises(ValueError, match="oversold"):
            RSIStrategy(oversold=75.0, overbought=70.0)


class TestRSIStrategyName:
    """name 프로퍼티 관련 테스트."""

    def test_name_format_default(self) -> None:
        """기본값으로 초기화한 전략의 name이 올바른 형식인지 확인."""
        strategy = RSIStrategy()
        assert strategy.name == "RSI_14_30.0_70.0"

    def test_name_format_custom(self) -> None:
        """커스텀 값으로 초기화한 전략의 name 확인."""
        strategy = RSIStrategy(period=7, oversold=25.0, overbought=75.0)
        assert strategy.name == "RSI_7_25.0_75.0"


class TestRSIStrategySignals:
    """generate_signals 메서드 관련 테스트."""

    def test_generate_signals_returns_series(self, sample_df: pd.DataFrame) -> None:
        """반환값이 pd.Series인지 확인."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_df)
        assert isinstance(signals, pd.Series)

    def test_signals_are_binary(self, sample_df: pd.DataFrame) -> None:
        """신호 값이 0 또는 1만 포함하는지 확인."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_df)
        unique_values = set(signals.unique())
        assert unique_values.issubset({0, 1})

    def test_signals_length_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 길이가 입력 DataFrame과 동일한지 확인."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_df)
        assert len(signals) == len(sample_df)

    def test_signals_index_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 인덱스가 입력 DataFrame과 동일한지 확인."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_df)
        pd.testing.assert_index_equal(signals.index, sample_df.index)

    def test_insufficient_data_no_nan(self, sample_df_short: pd.DataFrame) -> None:
        """데이터 부족 시에도 NaN이 없는지 확인 (0으로 채워짐)."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_df_short)

        # 모든 값이 0 또는 1이어야 함 (NaN 없음)
        assert not signals.isna().any()
        assert all(v in {0, 1} for v in signals.values)

    def test_constant_prices_no_signal(self) -> None:
        """상수 가격일 때 신호가 0인지 확인 (gain=0, loss=0 → rs=NaN → rsi=NaN → 0)."""
        # 모든 Close 가격이 동일하면 diff=0 → gain=0, loss=0 → rs=NaN → rsi=NaN
        df = _make_sample_df(rows=60)
        strategy = RSIStrategy()
        signals = strategy.generate_signals(df)

        # 모든 값이 0이어야 함 (상수 가격이므로 RSI는 계산 불가 → NaN → 0)
        assert (signals == 0).all()
