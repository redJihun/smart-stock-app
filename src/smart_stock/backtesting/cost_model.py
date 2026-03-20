"""거래 비용 모델 모듈."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradingCost:
    """거래 비용 모델 (수수료 + 세금 + 슬리피지).

    한국 주식 기본값 기준:
    - commission_rate: 0.00015 (0.015%, 매수/매도 각각 적용)
    - tax_rate: 0.0018 (0.18%, 매도 시에만 적용)
    - slippage_rate: 0.0005 (0.05%, 단방향, 매수/매도 각각)

    Parameters
    ----------
    commission_rate : float, optional
        증권사 수수료율 (기본값: 0.00015)
    tax_rate : float, optional
        증권거래세율 (기본값: 0.0018, 매도 시만)
    slippage_rate : float, optional
        슬리피지율 (기본값: 0.0005, 단방향)

    Raises
    ------
    ValueError
        어떤 비율이라도 음수인 경우
    """

    commission_rate: float = 0.00015
    tax_rate: float = 0.0018
    slippage_rate: float = 0.0005

    def __post_init__(self) -> None:
        """비율의 유효성을 검증합니다."""
        for name, val in [
            ("commission_rate", self.commission_rate),
            ("tax_rate", self.tax_rate),
            ("slippage_rate", self.slippage_rate),
        ]:
            if val < 0:
                raise ValueError(f"{name}은 0 이상이어야 합니다. 현재: {val}")

    def buy_cost_rate(self) -> float:
        """매수 시 총 비용율.

        Returns
        -------
        float
            commission_rate + slippage_rate
        """
        return self.commission_rate + self.slippage_rate

    def sell_cost_rate(self) -> float:
        """매도 시 총 비용율.

        Returns
        -------
        float
            commission_rate + tax_rate + slippage_rate
        """
        return self.commission_rate + self.tax_rate + self.slippage_rate
