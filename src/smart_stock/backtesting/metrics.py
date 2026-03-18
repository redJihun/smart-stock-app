"""백테스팅 성과 지표 계산 모듈."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def total_return(portfolio: pd.Series, initial_capital: float) -> float:
    """포트폴리오의 총 수익률을 계산합니다.

    Parameters
    ----------
    portfolio : pd.Series
        포트폴리오 자산 가치 시계열
    initial_capital : float
        초기 자본금

    Returns
    -------
    float
        총 수익률 (%)

    Raises
    ------
    ValueError
        포트폴리오가 비어있거나 초기자본이 0 이하인 경우
    """
    if portfolio.empty:
        raise ValueError("포트폴리오가 비어있습니다.")
    if initial_capital <= 0:
        raise ValueError("초기자본은 0보다 커야 합니다.")

    final_value = portfolio.iloc[-1]
    return float((final_value / initial_capital - 1) * 100)


def max_drawdown(portfolio: pd.Series) -> float:
    """포트폴리오의 최대 낙폭을 계산합니다.

    Parameters
    ----------
    portfolio : pd.Series
        포트폴리오 자산 가치 시계열

    Returns
    -------
    float
        최대 낙폭 (%, 음수 값)

    Raises
    ------
    ValueError
        포트폴리오가 비어있는 경우
    """
    if portfolio.empty:
        raise ValueError("포트폴리오가 비어있습니다.")

    drawdown = (portfolio - portfolio.cummax()) / portfolio.cummax()
    return float(drawdown.min() * 100)


def sharpe_ratio(
    portfolio: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    """포트폴리오의 연간화 샤프 지수를 계산합니다.

    Parameters
    ----------
    portfolio : pd.Series
        포트폴리오 자산 가치 시계열
    risk_free_rate : float, optional
        무위험 이자율 (연간, 기본값: 0.0)

    Returns
    -------
    float
        연간화 샤프 지수

    Raises
    ------
    ValueError
        포트폴리오가 2개 미만의 값을 가지는 경우
    """
    if len(portfolio) < 2:
        raise ValueError("샤프 지수 계산을 위해 최소 2개의 값이 필요합니다.")

    daily_returns = portfolio.pct_change().dropna()

    if daily_returns.empty:
        raise ValueError("일일 수익률이 비어있습니다.")

    mean_return = daily_returns.mean()
    std_return = daily_returns.std()

    if std_return == 0:
        return 0.0

    excess_return = mean_return - risk_free_rate / 252
    return excess_return / std_return * math.sqrt(252)


def win_rate(trade_returns: list[float]) -> float:
    """거래의 승률을 계산합니다.

    Parameters
    ----------
    trade_returns : list[float]
        거래별 수익/손실 리스트

    Returns
    -------
    float
        승률 (%)

    Notes
    -----
    빈 리스트 입력 시 NaN을 반환합니다.
    """
    if not trade_returns:
        return float("nan")

    winning_trades = sum(1 for r in trade_returns if r > 0)
    return (winning_trades / len(trade_returns)) * 100
