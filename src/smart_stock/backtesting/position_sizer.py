"""포지션 사이징 모듈."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PositionSizer(ABC):
    """포지션 사이징 추상 기반 클래스.

    Parameters
    ----------
    (없음 — 서브클래스에서 정의)

    Notes
    -----
    calculate()는 항상 [0.0, 1.0] 범위의 투입 비율(fraction)을 반환해야 한다.
    """

    @abstractmethod
    def calculate(
        self,
        portfolio_value: float,
        trade_returns: list[float],
    ) -> float:
        """투입 비율(fraction)을 계산한다.

        Parameters
        ----------
        portfolio_value : float
            현재 포트폴리오 가치 (단위: 원)
        trade_returns : list[float]
            지금까지 완결된 거래 수익률 리스트 (소수, 예: 0.05 = 5%)

        Returns
        -------
        float
            투입 비율 [0.0, 1.0]
        """


class FixedAmountSizer(PositionSizer):
    """매 거래마다 고정 금액을 투입하는 사이저.

    Parameters
    ----------
    amount : float
        매 거래마다 투입할 고정 금액 (양수여야 함)

    Raises
    ------
    ValueError
        amount <= 0인 경우
    """

    def __init__(self, amount: float) -> None:
        """초기화.

        Parameters
        ----------
        amount : float
            매 거래마다 투입할 고정 금액

        Raises
        ------
        ValueError
            amount <= 0인 경우
        """
        if amount <= 0:
            raise ValueError(f"amount는 0보다 커야 합니다. 현재: {amount}")
        self.amount = amount

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        """투입 비율을 계산한다.

        Parameters
        ----------
        portfolio_value : float
            현재 포트폴리오 가치
        trade_returns : list[float]
            거래 수익률 리스트 (사용되지 않음)

        Returns
        -------
        float
            투입 비율 [0.0, 1.0]
        """
        if portfolio_value <= 0:
            return 0.0
        return min(self.amount / portfolio_value, 1.0)


class FixedFractionSizer(PositionSizer):
    """매 거래마다 포트폴리오의 고정 비율을 투입하는 사이저.

    Parameters
    ----------
    fraction : float
        투입 비율 (0 초과 1 이하)

    Raises
    ------
    ValueError
        fraction <= 0 또는 fraction > 1.0인 경우
    """

    def __init__(self, fraction: float) -> None:
        """초기화.

        Parameters
        ----------
        fraction : float
            투입 비율

        Raises
        ------
        ValueError
            fraction <= 0 또는 fraction > 1.0인 경우
        """
        if fraction <= 0 or fraction > 1.0:
            raise ValueError(f"fraction은 (0, 1] 범위여야 합니다. 현재: {fraction}")
        self.fraction = fraction

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        """투입 비율을 계산한다.

        Parameters
        ----------
        portfolio_value : float
            현재 포트폴리오 가치 (사용되지 않음)
        trade_returns : list[float]
            거래 수익률 리스트 (사용되지 않음)

        Returns
        -------
        float
            항상 고정된 비율 반환
        """
        return self.fraction


class KellyCriterionSizer(PositionSizer):
    """Kelly Criterion으로 최적 투입 비율을 계산하는 사이저.

    f* = (b * p - q) / b
    b = 평균 이익 / 평균 손실 비율
    p = 승률, q = 1 - p

    Parameters
    ----------
    max_fraction : float, optional
        최대 투입 비율 상한 (기본값: 0.25)
        과레버리지 방지를 위해 f* > max_fraction이면 max_fraction으로 클리핑

    Raises
    ------
    ValueError
        max_fraction <= 0 또는 max_fraction > 1.0인 경우

    Notes
    -----
    과거 거래 데이터가 2개 미만이면 0.0 반환 (통계적 불충분)
    f* < 0 (기대값 음수 전략)이면 0.0으로 클리핑
    """

    def __init__(self, max_fraction: float = 0.25) -> None:
        """초기화.

        Parameters
        ----------
        max_fraction : float, optional
            최대 투입 비율 상한 (기본값: 0.25)

        Raises
        ------
        ValueError
            max_fraction <= 0 또는 max_fraction > 1.0인 경우
        """
        if max_fraction <= 0 or max_fraction > 1.0:
            raise ValueError(
                f"max_fraction은 (0, 1] 범위여야 합니다. 현재: {max_fraction}"
            )
        self.max_fraction = max_fraction

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        """투입 비율을 계산한다.

        Parameters
        ----------
        portfolio_value : float
            현재 포트폴리오 가치 (사용되지 않음)
        trade_returns : list[float]
            거래 수익률 리스트

        Returns
        -------
        float
            Kelly Criterion 기반 투입 비율 [0.0, max_fraction]
        """
        returns = [r for r in trade_returns if r != 0.0]
        if len(returns) < 2:
            return 0.0

        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]

        if not losses:
            return self.max_fraction
        if not wins:
            return 0.0

        p = len(wins) / len(returns)
        q = 1.0 - p
        avg_win = sum(wins) / len(wins)
        avg_loss = abs(sum(losses) / len(losses))
        b = avg_win / avg_loss

        f_star = (b * p - q) / b
        return max(0.0, min(f_star, self.max_fraction))
