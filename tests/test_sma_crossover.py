from __future__ import annotations

import pandas as pd
import pytest

from smart_stock.strategies.sma_crossover import SMAcrossoverStrategy


def _make_sample_df(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV 샘플 DataFrame을 생성한다.

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60, SMA 계산에 충분함)

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


class TestSMAcrossoverStrategyInit:
    """초기화 관련 테스트."""

    def test_short_window_longer_than_long_raises(self) -> None:
        """short_window >= long_window인 경우 ValueError 발생."""
        with pytest.raises(ValueError, match="short_window"):
            SMAcrossoverStrategy(short_window=50, long_window=50)

        with pytest.raises(ValueError, match="short_window"):
            SMAcrossoverStrategy(short_window=60, long_window=50)


class TestSMAcrossoverStrategyName:
    """name 프로퍼티 관련 테스트."""

    def test_name_format_default(self) -> None:
        """기본값으로 초기화한 전략의 name이 올바른 형식인지 확인."""
        strategy = SMAcrossoverStrategy()
        assert strategy.name == "SMA_20_50"

    def test_name_format_custom(self) -> None:
        """커스텀 윈도우 값으로 초기화한 전략의 name 확인."""
        strategy = SMAcrossoverStrategy(short_window=10, long_window=30)
        assert strategy.name == "SMA_10_30"


class TestSMAcrossoverStrategySignals:
    """generate_signals 메서드 관련 테스트."""

    def test_generate_signals_returns_series(self, sample_df: pd.DataFrame) -> None:
        """반환값이 pd.Series인지 확인."""
        strategy = SMAcrossoverStrategy()
        signals = strategy.generate_signals(sample_df)
        assert isinstance(signals, pd.Series)

    def test_signals_length_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 길이가 입력 DataFrame과 동일한지 확인."""
        strategy = SMAcrossoverStrategy()
        signals = strategy.generate_signals(sample_df)
        assert len(signals) == len(sample_df)

    def test_signals_index_matches_input(self, sample_df: pd.DataFrame) -> None:
        """신호 시리즈의 인덱스가 입력 DataFrame과 동일한지 확인."""
        strategy = SMAcrossoverStrategy()
        signals = strategy.generate_signals(sample_df)
        pd.testing.assert_index_equal(signals.index, sample_df.index)

    def test_signals_are_binary(self, sample_df: pd.DataFrame) -> None:
        """신호 값이 0 또는 1만 포함하는지 확인."""
        strategy = SMAcrossoverStrategy()
        signals = strategy.generate_signals(sample_df)
        unique_values = set(signals.unique())
        assert unique_values.issubset({0, 1})

    def test_insufficient_data_returns_zeros(
        self, sample_df_short: pd.DataFrame
    ) -> None:
        """데이터 부족(long_window > rows)인 경우 초기 부분이 0으로 채워지는지 확인."""
        # long_window(50) > rows(5)이므로 초기 부분이 NaN이 되어 0으로 채워짐
        strategy = SMAcrossoverStrategy(short_window=2, long_window=5)
        signals = strategy.generate_signals(sample_df_short)

        # 모든 값이 0 또는 1이어야 함 (NaN 없음)
        assert not signals.isna().any()
        assert all(v in {0, 1} for v in signals.values)

    def test_crossover_logic_constant_prices(self) -> None:
        """상수 가격일 때 short_SMA == long_SMA → 신호 0인지 확인."""
        # 모든 Close 가격이 동일하면 모든 SMA가 동일하므로 short > long이 false
        df = _make_sample_df(rows=60)
        strategy = SMAcrossoverStrategy(short_window=20, long_window=50)
        signals = strategy.generate_signals(df)

        # 모든 값이 0이어야 함 (상수 가격이므로 short == long)
        assert (signals == 0).all()

    def test_crossover_logic_increasing_prices(self) -> None:
        """증가하는 가격일 때 신호가 1로 수렴하는지 확인."""
        # 증가하는 가격 데이터 생성
        idx = pd.date_range("2024-01-02", periods=60, freq="B")
        close_prices = [70000.0 + i * 10 for i in range(60)]
        df = pd.DataFrame(
            {
                "Open": close_prices,
                "High": [p + 500 for p in close_prices],
                "Low": [p - 500 for p in close_prices],
                "Close": close_prices,
                "Volume": [1_000_000] * 60,
            },
            index=idx,
        )

        strategy = SMAcrossoverStrategy(short_window=20, long_window=50)
        signals = strategy.generate_signals(df)

        # rolling().mean()은 window번째(0-based 인덱스는 window-1)부터 계산됨
        # long_window=50이므로 인덱스 49부터 long_SMA 계산 가능
        # 처음 49개(인덱스 0-48)까지는 신호 0
        # 50번째(인덱스 49)부터는 short_SMA > long_SMA → 1 (증가 추세)
        assert (signals.iloc[:49] == 0).all()
        assert (signals.iloc[49:] == 1).all()
