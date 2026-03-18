from __future__ import annotations

import pandas as pd

from smart_stock.strategies.base_strategy import BaseStrategy


class CompositeStrategy:
    """
    복합 전략 (여러 전략의 가중 앙상블).

    여러 개의 기본 전략을 결합하여 하나의 통합 신호를 생성한다.
    각 전략의 신호를 가중 평균하여 연속값(0.0~1.0)으로 표현하고,
    임계값과 비교하여 최종 이진 신호(0/1)를 반환한다.

    사용 예:
        strategies = [
            (SMAcrossoverStrategy(20, 50), 0.3),
            (RSIStrategy(period=14), 0.5),
            (MACDStrategy(), 0.2),
        ]
        composite = CompositeStrategy(strategies, threshold=0.6)
        signals = composite.generate_signals(df)
    """

    def __init__(
        self,
        strategies: list[tuple[BaseStrategy, float]],
        threshold: float = 0.5,
        name: str = "composite",
    ) -> None:
        """복합 전략을 초기화한다.

        Parameters
        ----------
        strategies : list[tuple[BaseStrategy, float]]
            (전략 인스턴스, 가중치) 튜플의 리스트.
            각 전략은 BaseStrategy의 인스턴스여야 한다.

        threshold : float, optional
            신호 이진화 임계값 (기본값: 0.5).
            generate_signals_strength() >= threshold이면 신호 1,
            미만이면 신호 0.

        name : str, optional
            복합 전략의 이름 (기본값: "composite")

        Raises
        ------
        ValueError
            - strategies가 빈 리스트인 경우
            - 어떤 가중치가 0 이하인 경우
            - threshold가 [0.0, 1.0] 범위를 벗어나는 경우
        """
        if not strategies:
            raise ValueError("strategies는 빈 리스트일 수 없습니다.")

        for strategy, weight in strategies:
            if weight <= 0:
                msg = (
                    f"가중치는 양수여야 합니다. 전략 {strategy.name}의 가중치: {weight}"
                )
                raise ValueError(msg)

        if not (0.0 <= threshold <= 1.0):
            msg = f"threshold는 [0.0, 1.0] 범위 내여야 합니다. 현재: {threshold}"
            raise ValueError(msg)

        self.strategies = strategies
        self.threshold = threshold
        self._name = name

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다.

        Returns
        -------
        str
            복합 전략의 이름
        """
        return self._name

    def generate_signals_strength(self, df: pd.DataFrame) -> pd.Series:
        """
        각 전략의 신호를 가중 평균하여 강도(연속값)를 계산한다.

        각 전략에서 생성된 이진 신호(0/1)를 가중치로 평균하여
        0.0~1.0 범위의 연속값을 반환한다.

        공식:
            strength = sum(signal_i * weight_i) / sum(weight_i)

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터. 필수 컬럼: ["Open", "High", "Low", "Close", "Volume"]
            인덱스는 DatetimeIndex여야 한다.

        Returns
        -------
        pd.Series
            신호 강도 Series. 값은 0.0~1.0 범위이고,
            인덱스는 입력 df와 동일하다.

        Raises
        ------
        ValueError
            필수 컬럼이 없거나 인덱스가 DatetimeIndex가 아닌 경우
        """
        # 각 전략의 신호 수집
        signals_list = []
        weights_list = []

        for strategy, weight in self.strategies:
            signals = strategy.generate_signals(df)
            signals_list.append(signals.astype(float))
            weights_list.append(weight)

        # 가중 평균 계산
        total_weight = sum(weights_list)

        # 가중 합계 계산
        weighted_sum = pd.Series(0.0, index=df.index)
        for sig, w in zip(signals_list, weights_list, strict=True):
            weighted_sum += sig * w

        strength: pd.Series = weighted_sum / total_weight

        return strength

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        통합 신호를 생성한다.

        generate_signals_strength()의 결과를 임계값과 비교하여
        이진 신호(0/1)로 변환한다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터. 필수 컬럼: ["Open", "High", "Low", "Close", "Volume"]
            인덱스는 DatetimeIndex여야 한다.

        Returns
        -------
        pd.Series
            통합 신호 Series. 값은 0(신호 없음) 또는 1(신호 있음)이고,
            인덱스는 입력 df와 동일하다.

        Raises
        ------
        ValueError
            필수 컬럼이 없거나 인덱스가 DatetimeIndex가 아닌 경우
        """
        strength = self.generate_signals_strength(df)
        signals = (strength >= self.threshold).astype(int)
        return signals
