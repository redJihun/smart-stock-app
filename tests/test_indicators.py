from __future__ import annotations

import pandas as pd
import pytest

from smart_stock.analysis.indicators import (
    atr,
    bollinger_bands,
    ema,
    macd,
    obv,
    rsi,
    sma,
    stochastic,
)


def _make_ohlcv(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV 샘플 DataFrame을 생성한다.

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60, 지표 계산에 충분함)

    Returns
    -------
    pd.DataFrame
        OHLCV 데이터를 포함하는 DataFrame
    """
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    # 단조 증가 추세로 구성 (진동폭 있음)
    close_prices = [70000.0 + i * 10.0 + (i % 3 - 1) * 50.0 for i in range(rows)]
    high_prices = [c + 1000.0 for c in close_prices]
    low_prices = [c - 1000.0 for c in close_prices]

    return pd.DataFrame(
        {
            "Open": close_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": [1_000_000] * rows,
        },
        index=idx,
    )


@pytest.fixture()
def sample_ohlcv() -> pd.DataFrame:
    """기본 샘플 OHLCV DataFrame fixture."""
    return _make_ohlcv()


@pytest.fixture()
def sample_close(sample_ohlcv: pd.DataFrame) -> pd.Series:
    """Close 시리즈 fixture."""
    return sample_ohlcv["Close"]


@pytest.fixture()
def sample_high(sample_ohlcv: pd.DataFrame) -> pd.Series:
    """High 시리즈 fixture."""
    return sample_ohlcv["High"]


@pytest.fixture()
def sample_low(sample_ohlcv: pd.DataFrame) -> pd.Series:
    """Low 시리즈 fixture."""
    return sample_ohlcv["Low"]


@pytest.fixture()
def sample_volume(sample_ohlcv: pd.DataFrame) -> pd.Series:
    """Volume 시리즈 fixture."""
    return sample_ohlcv["Volume"]


class TestSMA:
    """SMA 함수 관련 테스트."""

    def test_sma_returns_series(self, sample_close: pd.Series) -> None:
        """반환값이 pd.Series인지 확인."""
        result = sma(sample_close, window=20)
        assert isinstance(result, pd.Series)

    def test_sma_length_matches_input(self, sample_close: pd.Series) -> None:
        """SMA 시리즈의 길이가 입력과 동일한지 확인."""
        result = sma(sample_close, window=20)
        assert len(result) == len(sample_close)

    def test_sma_index_matches_input(self, sample_close: pd.Series) -> None:
        """SMA 인덱스가 입력과 동일한지 확인."""
        result = sma(sample_close, window=20)
        pd.testing.assert_index_equal(result.index, sample_close.index)

    def test_sma_has_nans_in_warmup(self, sample_close: pd.Series) -> None:
        """초기 window-1개 값이 NaN인지 확인 (warm-up)."""
        result = sma(sample_close, window=20)
        assert result.iloc[:19].isna().all()

    def test_sma_no_nan_after_warmup(self, sample_close: pd.Series) -> None:
        """warm-up 이후 NaN이 없는지 확인."""
        result = sma(sample_close, window=20)
        assert not result.iloc[19:].isna().any()


class TestEMA:
    """EMA 함수 관련 테스트."""

    def test_ema_returns_series(self, sample_close: pd.Series) -> None:
        """반환값이 pd.Series인지 확인."""
        result = ema(sample_close, span=12)
        assert isinstance(result, pd.Series)

    def test_ema_length_matches_input(self, sample_close: pd.Series) -> None:
        """EMA 시리즈의 길이가 입력과 동일한지 확인."""
        result = ema(sample_close, span=12)
        assert len(result) == len(sample_close)

    def test_ema_index_matches_input(self, sample_close: pd.Series) -> None:
        """EMA 인덱스가 입력과 동일한지 확인."""
        result = ema(sample_close, span=12)
        pd.testing.assert_index_equal(result.index, sample_close.index)

    def test_ema_no_nan_values(self, sample_close: pd.Series) -> None:
        """EMA에 NaN이 없는지 확인."""
        result = ema(sample_close, span=12)
        assert not result.isna().any()


class TestRSI:
    """RSI 함수 관련 테스트."""

    def test_rsi_returns_series(self, sample_close: pd.Series) -> None:
        """반환값이 pd.Series인지 확인."""
        result = rsi(sample_close, period=14)
        assert isinstance(result, pd.Series)

    def test_rsi_length_matches_input(self, sample_close: pd.Series) -> None:
        """RSI 시리즈의 길이가 입력과 동일한지 확인."""
        result = rsi(sample_close, period=14)
        assert len(result) == len(sample_close)

    def test_rsi_index_matches_input(self, sample_close: pd.Series) -> None:
        """RSI 인덱스가 입력과 동일한지 확인."""
        result = rsi(sample_close, period=14)
        pd.testing.assert_index_equal(result.index, sample_close.index)

    def test_rsi_in_range_0_100(self, sample_close: pd.Series) -> None:
        """RSI 값이 0~100 범위 내인지 확인 (NaN 제외)."""
        result = rsi(sample_close, period=14)
        # NaN을 제외하고 검사
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_rsi_no_error_on_constant_prices(self) -> None:
        """상수 가격에서 0으로 나누기 에러가 없는지 확인."""
        # 모든 Close가 동일한 경우
        const_close = pd.Series(
            [70000.0] * 60, index=pd.date_range("2024-01-02", periods=60, freq="B")
        )
        result = rsi(const_close, period=14)
        assert isinstance(result, pd.Series)
        assert len(result) == len(const_close)


class TestMACD:
    """MACD 함수 관련 테스트."""

    def test_macd_returns_dataframe(self, sample_close: pd.Series) -> None:
        """반환값이 pd.DataFrame인지 확인."""
        result = macd(sample_close, fast=12, slow=26, signal=9)
        assert isinstance(result, pd.DataFrame)

    def test_macd_has_correct_columns(self, sample_close: pd.Series) -> None:
        """MACD 컬럼명이 올바른지 확인."""
        result = macd(sample_close, fast=12, slow=26, signal=9)
        assert set(result.columns) == {"macd", "signal", "histogram"}

    def test_macd_length_matches_input(self, sample_close: pd.Series) -> None:
        """MACD 길이가 입력과 동일한지 확인."""
        result = macd(sample_close, fast=12, slow=26, signal=9)
        assert len(result) == len(sample_close)

    def test_macd_histogram_equals_macd_minus_signal(
        self, sample_close: pd.Series
    ) -> None:
        """histogram = macd - signal 검증."""
        result = macd(sample_close, fast=12, slow=26, signal=9)
        # NaN을 제외하고 검사
        valid_mask = result.notna().all(axis=1)
        pd.testing.assert_series_equal(
            result.loc[valid_mask, "histogram"],
            result.loc[valid_mask, "macd"] - result.loc[valid_mask, "signal"],
            check_names=False,
        )


class TestStochastic:
    """스토캐스틱 오실레이터 함수 관련 테스트."""

    def test_stochastic_returns_dataframe(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """반환값이 pd.DataFrame인지 확인."""
        result = stochastic(sample_high, sample_low, sample_close, k=14, d=3)
        assert isinstance(result, pd.DataFrame)

    def test_stochastic_has_correct_columns(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """스토캐스틱 컬럼명이 올바른지 확인."""
        result = stochastic(sample_high, sample_low, sample_close, k=14, d=3)
        assert set(result.columns) == {"k", "d"}

    def test_stochastic_length_matches_input(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """스토캐스틱 길이가 입력과 동일한지 확인."""
        result = stochastic(sample_high, sample_low, sample_close, k=14, d=3)
        assert len(result) == len(sample_high)

    def test_stochastic_k_in_range_0_100(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """K 값이 0~100 범위 내인지 확인 (NaN 제외)."""
        result = stochastic(sample_high, sample_low, sample_close, k=14, d=3)
        valid = result["k"].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()


class TestBollingerBands:
    """볼린저 밴드 함수 관련 테스트."""

    def test_bollinger_bands_returns_dataframe(self, sample_close: pd.Series) -> None:
        """반환값이 pd.DataFrame인지 확인."""
        result = bollinger_bands(sample_close, window=20, std_dev=2.0)
        assert isinstance(result, pd.DataFrame)

    def test_bollinger_bands_has_correct_columns(self, sample_close: pd.Series) -> None:
        """볼린저 밴드 컬럼명이 올바른지 확인."""
        result = bollinger_bands(sample_close, window=20, std_dev=2.0)
        assert set(result.columns) == {"middle", "upper", "lower", "bandwidth"}

    def test_bollinger_bands_length_matches_input(
        self, sample_close: pd.Series
    ) -> None:
        """볼린저 밴드 길이가 입력과 동일한지 확인."""
        result = bollinger_bands(sample_close, window=20, std_dev=2.0)
        assert len(result) == len(sample_close)

    def test_bollinger_bands_relationship(self, sample_close: pd.Series) -> None:
        """upper >= middle >= lower 관계 확인."""
        result = bollinger_bands(sample_close, window=20, std_dev=2.0)
        valid_mask = result.notna().all(axis=1)
        valid = result.loc[valid_mask]

        assert (valid["upper"] >= valid["middle"]).all()
        assert (valid["middle"] >= valid["lower"]).all()


class TestATR:
    """ATR 함수 관련 테스트."""

    def test_atr_returns_series(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """반환값이 pd.Series인지 확인."""
        result = atr(sample_high, sample_low, sample_close, period=14)
        assert isinstance(result, pd.Series)

    def test_atr_length_matches_input(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """ATR 길이가 입력과 동일한지 확인."""
        result = atr(sample_high, sample_low, sample_close, period=14)
        assert len(result) == len(sample_high)

    def test_atr_positive_values(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """ATR이 양수인지 확인 (NaN 제외)."""
        result = atr(sample_high, sample_low, sample_close, period=14)
        valid = result.dropna()
        assert (valid >= 0).all()

    def test_atr_index_matches_input(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """ATR 인덱스가 입력과 동일한지 확인."""
        result = atr(sample_high, sample_low, sample_close, period=14)
        pd.testing.assert_index_equal(result.index, sample_high.index)


class TestOBV:
    """OBV 함수 관련 테스트."""

    def test_obv_returns_series(
        self, sample_close: pd.Series, sample_volume: pd.Series
    ) -> None:
        """반환값이 pd.Series인지 확인."""
        result = obv(sample_close, sample_volume)
        assert isinstance(result, pd.Series)

    def test_obv_length_matches_input(
        self, sample_close: pd.Series, sample_volume: pd.Series
    ) -> None:
        """OBV 길이가 입력과 동일한지 확인."""
        result = obv(sample_close, sample_volume)
        assert len(result) == len(sample_close)

    def test_obv_index_matches_input(
        self, sample_close: pd.Series, sample_volume: pd.Series
    ) -> None:
        """OBV 인덱스가 입력과 동일한지 확인."""
        result = obv(sample_close, sample_volume)
        pd.testing.assert_index_equal(result.index, sample_close.index)

    def test_obv_cumsum_property(
        self, sample_close: pd.Series, sample_volume: pd.Series
    ) -> None:
        """OBV가 누적합 성질을 가지는지 확인 (증가 추세)."""
        result = obv(sample_close, sample_volume)
        # Close가 증가 추세이므로 OBV도 대체로 증가해야 함
        # 초기값과 마지막값 비교
        assert result.iloc[-1] >= result.iloc[0]


class TestValidation:
    """파라미터 유효성 검증 테스트."""

    def test_sma_invalid_window_raises(self, sample_close: pd.Series) -> None:
        """window <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            sma(sample_close, window=0)

        with pytest.raises(ValueError):
            sma(sample_close, window=-1)

    def test_ema_invalid_span_raises(self, sample_close: pd.Series) -> None:
        """span <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            ema(sample_close, span=0)

        with pytest.raises(ValueError):
            ema(sample_close, span=-1)

    def test_rsi_invalid_period_raises(self, sample_close: pd.Series) -> None:
        """period <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            rsi(sample_close, period=0)

        with pytest.raises(ValueError):
            rsi(sample_close, period=-1)

    def test_macd_invalid_fast_raises(self, sample_close: pd.Series) -> None:
        """fast <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            macd(sample_close, fast=0, slow=26, signal=9)

    def test_macd_invalid_slow_raises(self, sample_close: pd.Series) -> None:
        """slow <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            macd(sample_close, fast=12, slow=0, signal=9)

    def test_macd_invalid_signal_raises(self, sample_close: pd.Series) -> None:
        """signal <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            macd(sample_close, fast=12, slow=26, signal=0)

    def test_stochastic_invalid_k_raises(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """k <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            stochastic(sample_high, sample_low, sample_close, k=0, d=3)

    def test_stochastic_invalid_d_raises(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """d <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            stochastic(sample_high, sample_low, sample_close, k=14, d=0)

    def test_bollinger_bands_invalid_window_raises(
        self, sample_close: pd.Series
    ) -> None:
        """window <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            bollinger_bands(sample_close, window=0, std_dev=2.0)

    def test_bollinger_bands_invalid_std_dev_raises(
        self, sample_close: pd.Series
    ) -> None:
        """std_dev <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            bollinger_bands(sample_close, window=20, std_dev=0)

    def test_atr_invalid_period_raises(
        self, sample_high: pd.Series, sample_low: pd.Series, sample_close: pd.Series
    ) -> None:
        """period <= 0이면 ValueError 발생."""
        with pytest.raises(ValueError):
            atr(sample_high, sample_low, sample_close, period=0)
