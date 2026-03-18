"""CompositeStrategy 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.strategies.composite import CompositeStrategy
from smart_stock.strategies.macd_strategy import MACDStrategy
from smart_stock.strategies.rsi_strategy import RSIStrategy
from smart_stock.strategies.sma_crossover import (
    SMAcrossoverStrategy,
)

# ---------------------------------------------------------------------------
# 헬퍼 함수
# ---------------------------------------------------------------------------


def _make_ohlcv(rows: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV DataFrame 생성 (비즈니스 데이).

    Parameters
    ----------
    rows : int, optional
        생성할 행 수 (기본값: 60)

    Returns
    -------
    pd.DataFrame
        OHLCV 컬럼이 있는 DataFrame.
        인덱스는 DatetimeIndex (비즈니스 데이 기준).
    """
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    base_price = 70000.0

    return pd.DataFrame(
        {
            "Open": [base_price + i * 100 for i in range(rows)],
            "High": [base_price + i * 150 for i in range(rows)],
            "Low": [base_price + i * 50 for i in range(rows)],
            "Close": [base_price + i * 120 for i in range(rows)],
            "Volume": [100_000] * rows,
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """테스트용 60행 OHLCV DataFrame."""
    return _make_ohlcv(rows=60)


@pytest.fixture()
def sma_strategy() -> SMAcrossoverStrategy:
    """테스트용 SMA 전략 인스턴스."""
    return SMAcrossoverStrategy(short_window=20, long_window=50)


@pytest.fixture()
def rsi_strategy() -> RSIStrategy:
    """테스트용 RSI 전략 인스턴스."""
    return RSIStrategy(period=14)


@pytest.fixture()
def macd_strategy() -> MACDStrategy:
    """테스트용 MACD 전략 인스턴스."""
    return MACDStrategy()


# ---------------------------------------------------------------------------
# TestCompositeStrategyInit
# ---------------------------------------------------------------------------


class TestCompositeStrategyInit:
    """CompositeStrategy 초기화 테스트."""

    def test_empty_strategies_raises_valueerror(
        self, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """strategies가 빈 리스트이면 ValueError 발생."""
        with pytest.raises(ValueError, match="strategies는 빈 리스트일 수 없습니다"):
            CompositeStrategy(strategies=[])

    def test_negative_weight_raises_valueerror(
        self, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """가중치에 음수가 있으면 ValueError 발생."""
        with pytest.raises(ValueError, match="가중치는 양수여야 합니다"):
            CompositeStrategy(strategies=[(sma_strategy, -0.5)])

    def test_zero_weight_raises_valueerror(
        self, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """가중치가 0이면 ValueError 발생."""
        with pytest.raises(ValueError, match="가중치는 양수여야 합니다"):
            CompositeStrategy(strategies=[(sma_strategy, 0.0)])

    def test_threshold_below_zero_raises_valueerror(
        self, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """threshold < 0.0이면 ValueError 발생."""
        with pytest.raises(ValueError, match="threshold는"):
            CompositeStrategy(
                strategies=[(sma_strategy, 0.5)],
                threshold=-0.1,
            )

    def test_threshold_above_one_raises_valueerror(
        self, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """threshold > 1.0이면 ValueError 발생."""
        with pytest.raises(ValueError, match="threshold는"):
            CompositeStrategy(
                strategies=[(sma_strategy, 0.5)],
                threshold=1.1,
            )

    def test_valid_initialization(
        self,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
    ) -> None:
        """정상 파라미터로 초기화 성공."""
        composite = CompositeStrategy(
            strategies=[(sma_strategy, 0.3), (rsi_strategy, 0.7)],
            threshold=0.6,
        )
        assert composite.threshold == 0.6
        assert len(composite.strategies) == 2
        assert composite.name == "composite"

    def test_custom_name(self, sma_strategy: SMAcrossoverStrategy) -> None:
        """커스텀 이름 설정 확인."""
        composite = CompositeStrategy(
            strategies=[(sma_strategy, 1.0)],
            name="my_composite",
        )
        assert composite.name == "my_composite"


# ---------------------------------------------------------------------------
# TestGenerateSignalsStrength
# ---------------------------------------------------------------------------


class TestGenerateSignalsStrength:
    """generate_signals_strength 메서드 테스트."""

    def test_return_type_is_series(
        self, sample_df: pd.DataFrame, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """반환 타입이 pd.Series."""
        composite = CompositeStrategy(strategies=[(sma_strategy, 1.0)])
        result = composite.generate_signals_strength(sample_df)
        assert isinstance(result, pd.Series)

    def test_length_matches_input_df(
        self, sample_df: pd.DataFrame, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """반환 Series의 길이가 입력 df와 동일."""
        composite = CompositeStrategy(strategies=[(sma_strategy, 1.0)])
        result = composite.generate_signals_strength(sample_df)
        assert len(result) == len(sample_df)

    def test_values_in_range_zero_to_one(
        self,
        sample_df: pd.DataFrame,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
    ) -> None:
        """반환값이 [0.0, 1.0] 범위."""
        composite = CompositeStrategy(
            strategies=[(sma_strategy, 0.5), (rsi_strategy, 0.5)]
        )
        result = composite.generate_signals_strength(sample_df)
        assert (result >= 0.0).all()
        assert (result <= 1.0).all()

    def test_single_strategy_matches_strategy_signals(
        self, sample_df: pd.DataFrame, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """단일 전략(가중치 1.0)일 때 해당 전략의 신호와 일치."""
        composite = CompositeStrategy(strategies=[(sma_strategy, 1.0)])
        strength = composite.generate_signals_strength(sample_df)
        strategy_signals = sma_strategy.generate_signals(sample_df).astype(float)

        pd.testing.assert_series_equal(strength, strategy_signals, check_names=False)

    def test_all_strategies_one_signal_gives_strength_one(
        self, sample_df: pd.DataFrame
    ) -> None:
        """모든 전략이 1 신호 → 강도 = 1.0."""
        mock_strategy1 = MagicMock()
        mock_strategy1.generate_signals.return_value = pd.Series(
            [1] * len(sample_df), index=sample_df.index
        )

        mock_strategy2 = MagicMock()
        mock_strategy2.generate_signals.return_value = pd.Series(
            [1] * len(sample_df), index=sample_df.index
        )

        composite = CompositeStrategy(
            strategies=[
                (mock_strategy1, 0.5),
                (mock_strategy2, 0.5),
            ]
        )
        strength = composite.generate_signals_strength(sample_df)

        # 모든 값이 1.0이어야 함
        assert (strength == 1.0).all()

    def test_all_strategies_zero_signal_gives_strength_zero(
        self, sample_df: pd.DataFrame
    ) -> None:
        """모든 전략이 0 신호 → 강도 = 0.0."""
        mock_strategy1 = MagicMock()
        mock_strategy1.generate_signals.return_value = pd.Series(
            [0] * len(sample_df), index=sample_df.index
        )

        mock_strategy2 = MagicMock()
        mock_strategy2.generate_signals.return_value = pd.Series(
            [0] * len(sample_df), index=sample_df.index
        )

        composite = CompositeStrategy(
            strategies=[
                (mock_strategy1, 0.5),
                (mock_strategy2, 0.5),
            ]
        )
        strength = composite.generate_signals_strength(sample_df)

        # 모든 값이 0.0이어야 함
        assert (strength == 0.0).all()


# ---------------------------------------------------------------------------
# TestGenerateSignals
# ---------------------------------------------------------------------------


class TestGenerateSignals:
    """generate_signals 메서드 테스트."""

    def test_return_type_is_series(
        self, sample_df: pd.DataFrame, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """반환 타입이 pd.Series."""
        composite = CompositeStrategy(strategies=[(sma_strategy, 1.0)])
        result = composite.generate_signals(sample_df)
        assert isinstance(result, pd.Series)

    def test_return_values_are_binary(
        self,
        sample_df: pd.DataFrame,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
    ) -> None:
        """반환값이 {0, 1}만 포함 (이진)."""
        composite = CompositeStrategy(
            strategies=[(sma_strategy, 0.5), (rsi_strategy, 0.5)]
        )
        result = composite.generate_signals(sample_df)
        unique_values = set(result.unique())
        assert unique_values.issubset({0, 1})

    def test_threshold_zero_always_one(
        self, sample_df: pd.DataFrame, sma_strategy: SMAcrossoverStrategy
    ) -> None:
        """threshold=0.0이면 항상 1."""
        composite = CompositeStrategy(
            strategies=[(sma_strategy, 1.0)],
            threshold=0.0,
        )
        result = composite.generate_signals(sample_df)
        # strength >= 0.0은 항상 true이므로 모두 1
        assert (result == 1).all()

    def test_threshold_one_mostly_zero_for_mixed_signals(
        self, sample_df: pd.DataFrame
    ) -> None:
        """threshold=1.0일 때, 모든 전략이 동시에 1이 아니면 0."""
        # 일부는 1, 일부는 0인 신호를 생성하는 mock 전략
        mock_strategy1 = MagicMock()
        mock_strategy1.generate_signals.return_value = pd.Series(
            [1] * 30 + [0] * 30, index=sample_df.index
        )

        mock_strategy2 = MagicMock()
        mock_strategy2.generate_signals.return_value = pd.Series(
            [0] * 30 + [1] * 30, index=sample_df.index
        )

        composite = CompositeStrategy(
            strategies=[
                (mock_strategy1, 0.5),
                (mock_strategy2, 0.5),
            ],
            threshold=1.0,
        )
        result = composite.generate_signals(sample_df)

        # 두 전략이 동시에 1인 경우가 없으므로 강도 = 0.5 < 1.0, 모두 0
        assert (result == 0).all()

    def test_weight_change_affects_signals(self, sample_df: pd.DataFrame) -> None:
        """가중치 변경 시 신호가 달라질 수 있음."""
        # 신호가 다른 두 전략
        mock_strategy1 = MagicMock()
        mock_strategy1.generate_signals.return_value = pd.Series(
            [1] * len(sample_df), index=sample_df.index
        )

        mock_strategy2 = MagicMock()
        mock_strategy2.generate_signals.return_value = pd.Series(
            [0] * len(sample_df), index=sample_df.index
        )

        # 가중치: strategy1이 우세
        composite1 = CompositeStrategy(
            strategies=[
                (mock_strategy1, 0.9),
                (mock_strategy2, 0.1),
            ],
            threshold=0.5,
        )
        signals1 = composite1.generate_signals(sample_df)

        # 가중치: strategy2가 우세
        composite2 = CompositeStrategy(
            strategies=[
                (mock_strategy1, 0.1),
                (mock_strategy2, 0.9),
            ],
            threshold=0.5,
        )
        signals2 = composite2.generate_signals(sample_df)

        # 다른 신호가 나와야 함
        assert not signals1.equals(signals2)


# ---------------------------------------------------------------------------
# TestCompositeWithRealStrategies
# ---------------------------------------------------------------------------


class TestCompositeWithRealStrategies:
    """실제 전략 인스턴스와의 통합 테스트."""

    def test_sma_and_rsi_combination(
        self,
        sample_df: pd.DataFrame,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
    ) -> None:
        """SMA + RSI 결합 → 정상 실행."""
        composite = CompositeStrategy(
            strategies=[
                (sma_strategy, 0.6),
                (rsi_strategy, 0.4),
            ]
        )
        signals = composite.generate_signals(sample_df)

        # 신호가 반환되고 길이가 맞는지 확인
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(sample_df)
        assert set(signals.unique()).issubset({0, 1})

    def test_three_strategy_combination(
        self,
        sample_df: pd.DataFrame,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
        macd_strategy: MACDStrategy,
    ) -> None:
        """3개 전략 결합 → 정상 실행."""
        composite = CompositeStrategy(
            strategies=[
                (sma_strategy, 0.3),
                (rsi_strategy, 0.4),
                (macd_strategy, 0.3),
            ]
        )
        signals = composite.generate_signals(sample_df)

        assert isinstance(signals, pd.Series)
        assert len(signals) == len(sample_df)
        assert set(signals.unique()).issubset({0, 1})

    def test_index_matches_input_df(
        self,
        sample_df: pd.DataFrame,
        sma_strategy: SMAcrossoverStrategy,
        rsi_strategy: RSIStrategy,
    ) -> None:
        """반환된 신호의 인덱스가 입력 df와 동일."""
        composite = CompositeStrategy(
            strategies=[
                (sma_strategy, 0.5),
                (rsi_strategy, 0.5),
            ]
        )
        signals = composite.generate_signals(sample_df)

        pd.testing.assert_index_equal(signals.index, sample_df.index)
