from __future__ import annotations

import pandas as pd
import pytest

from smart_stock.strategies.bollinger_strategy import BollingerBandStrategy


def _make_sample_df(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV 샘플 DataFrame을 생성한다.

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60, 볼린저밴드 계산에 충분함)

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
def bb_strategy() -> BollingerBandStrategy:
    """기본값으로 초기화한 BollingerBandStrategy fixture."""
    return BollingerBandStrategy()


class TestBollingerBandStrategyInit:
    """초기화 관련 테스트."""

    def test_invalid_period_raises(self) -> None:
        """period < 2인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="period는 2 이상이어야 합니다"):
            BollingerBandStrategy(period=1)

    def test_invalid_num_std_raises(self) -> None:
        """num_std <= 0인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="num_std는 0보다 커야 합니다"):
            BollingerBandStrategy(num_std=0)


class TestBollingerBandStrategyName:
    """name 프로퍼티 관련 테스트."""

    def test_name_format_default(self) -> None:
        """기본값으로 초기화한 전략의 name이 올바른 형식인지 확인."""
        strategy = BollingerBandStrategy()
        assert strategy.name == "BB_20_2.0"

    def test_name_format_custom(self) -> None:
        """커스텀 기간과 표준편차로 초기화한 전략의 name 확인."""
        strategy = BollingerBandStrategy(period=10, num_std=1.5)
        assert strategy.name == "BB_10_1.5"


class TestBollingerBandStrategySignals:
    """generate_signals 메서드 관련 테스트."""

    def test_generate_signals_returns_series(self, sample_df: pd.DataFrame) -> None:
        """반환값이 pd.Series인지 확인."""
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(sample_df)
        assert isinstance(signals, pd.Series)

    def test_signals_are_binary(self, sample_df: pd.DataFrame) -> None:
        """신호 값이 0 또는 1만 포함하는지 확인."""
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(sample_df)
        unique_values = set(signals.unique())
        assert unique_values.issubset({0, 1})

    def test_signals_length_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 길이가 입력 DataFrame과 동일한지 확인."""
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(sample_df)
        assert len(signals) == len(sample_df)

    def test_signals_index_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 인덱스가 입력 DataFrame과 동일한지 확인."""
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(sample_df)
        pd.testing.assert_index_equal(signals.index, sample_df.index)

    def test_no_nan_in_signals(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈에 NaN이 없는지 확인."""
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(sample_df)
        assert not signals.isna().any()

    def test_constant_prices_no_signal(self) -> None:
        """상수 가격일 때 모든 신호가 0인지 확인.

        상수 가격이면 표준편차가 0이고, 하단 밴드 = 중단이 된다.
        Close < 하단이 항상 거짓이므로 신호는 모두 0이다.
        """
        df = _make_sample_df(rows=60)
        strategy = BollingerBandStrategy(period=20, num_std=2.0)
        signals = strategy.generate_signals(df)

        # 모든 값이 0이어야 함 (상수 가격이므로 Close < lower가 거짓)
        assert (signals == 0).all()
