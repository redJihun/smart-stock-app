"""백테스팅 엔진 모듈."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from smart_stock.backtesting.cost_model import TradingCost
from smart_stock.backtesting.metrics import (
    max_drawdown,
    sharpe_ratio,
    total_return,
    win_rate,
)
from smart_stock.backtesting.position_sizer import PositionSizer
from smart_stock.strategies.base_strategy import BaseStrategy


@dataclass
class BacktestResult:
    """백테스트 결과.

    Attributes
    ----------
    total_return : float
        총 수익률 (%)
    mdd : float
        최대 낙폭 (%, 음수)
    sharpe_ratio : float
        연간화 샤프 비율 (252일 기준)
    trade_count : int
        완결된 거래 수 (매수→매도 사이클)
    win_rate : float
        승률 (%, trade_count==0이면 NaN)
    portfolio : pd.Series
        일별 포트폴리오 가치 (DatetimeIndex)
    total_cost : float, optional
        총 거래 비용 금액 (초기 자본 대비, 기본값: 0.0)
    """

    total_return: float
    mdd: float
    sharpe_ratio: float
    trade_count: int
    win_rate: float
    portfolio: pd.Series
    total_cost: float = 0.0


class BacktestEngine:
    """백테스팅 엔진."""

    def __init__(
        self,
        initial_capital: float = 1_000_000.0,
        cost_model: TradingCost | None = None,
        position_sizer: PositionSizer | None = None,
    ) -> None:
        """초기화.

        Parameters
        ----------
        initial_capital : float, optional
            초기 자본금 (기본값: 1,000,000)
        cost_model : TradingCost | None, optional
            거래 비용 모델 (기본값: None, 비용 미적용)
        position_sizer : PositionSizer | None, optional
            포지션 사이징 전략 (기본값: None, 자본 100% 투입)

        Raises
        ------
        ValueError
            initial_capital이 0 이하인 경우
        """
        if initial_capital <= 0:
            raise ValueError("initial_capital은 0보다 커야 합니다.")
        self.initial_capital = initial_capital
        self.cost_model = cost_model
        self.position_sizer = position_sizer

    def run(self, df: pd.DataFrame, strategy: BaseStrategy) -> BacktestResult:
        """백테스트를 실행하고 결과를 반환합니다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터 (Close 필수)
        strategy : BaseStrategy
            거래 전략 객체

        Returns
        -------
        BacktestResult
            백테스트 결과

        Raises
        ------
        ValueError
            데이터가 비어있거나 필수 열이 없는 경우
        """
        signals = strategy.generate_signals(df)
        portfolio, total_cost = self._build_portfolio(df, signals)
        trade_returns = self._extract_trades(df, signals)

        return BacktestResult(
            total_return=total_return(portfolio, self.initial_capital),
            mdd=max_drawdown(portfolio),
            sharpe_ratio=sharpe_ratio(portfolio),
            trade_count=len(trade_returns),
            win_rate=win_rate(trade_returns),
            portfolio=portfolio,
            total_cost=total_cost,
        )

    def _compute_sized_position(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
    ) -> pd.Series:
        """PositionSizer를 적용하여 포지션 비율 시계열을 계산합니다.

        거래 진입 시점마다 PositionSizer.calculate()를 호출하여
        해당 거래의 투입 비율을 결정합니다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터
        signals : pd.Series
            거래 신호 (0 또는 1)

        Returns
        -------
        pd.Series
            포지션 비율 시계열 (0.0~1.0)
        """
        sizer = self.position_sizer
        assert sizer is not None

        shifted = signals.shift(1).fillna(0)
        pos_diff = shifted.diff().fillna(0)

        fractions = pd.Series(0.0, index=df.index)
        completed_trade_returns: list[float] = []
        current_fraction = 0.0
        entry_price: float | None = None

        for idx in df.index:
            diff = float(pos_diff.loc[idx])
            if diff > 0:
                current_fraction = sizer.calculate(
                    self.initial_capital, completed_trade_returns
                )
                entry_price = float(df["Close"].loc[idx])
            elif diff < 0:
                if entry_price is not None:
                    trade_ret = float(df["Close"].loc[idx]) / entry_price - 1.0
                    completed_trade_returns.append(trade_ret)
                current_fraction = 0.0
                entry_price = None
            fractions.loc[idx] = current_fraction

        return fractions

    def _build_portfolio(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
    ) -> tuple[pd.Series, float]:
        """포트폴리오 가치 시계열과 총 비용 금액을 계산합니다.

        look-ahead bias를 방지하기 위해 시그널을 1일 지연(shift(1))해 적용합니다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터
        signals : pd.Series
            거래 신호 (0 또는 1)

        Returns
        -------
        tuple[pd.Series, float]
            (일별 포트폴리오 가치, 총 거래 비용 금액)
        """
        if self.position_sizer is not None:
            position = self._compute_sized_position(df, signals)
        else:
            position = signals.shift(1).fillna(0)
        pos_diff = position.diff().fillna(0)
        daily_returns = df["Close"].pct_change().fillna(0)
        strategy_returns = position * daily_returns

        total_cost = 0.0
        if self.cost_model is not None:
            cost_returns = pd.Series(0.0, index=df.index)
            cost_returns[pos_diff > 0] = -self.cost_model.buy_cost_rate()
            cost_returns[pos_diff < 0] = -self.cost_model.sell_cost_rate()
            strategy_returns = strategy_returns + cost_returns
            # 총 비용 금액 = 비용율 합계 × 초기 자본 (근사값)
            total_cost = float(cost_returns.abs().sum() * self.initial_capital)

        portfolio = self.initial_capital * (1 + strategy_returns).cumprod()
        return portfolio, total_cost

    def _extract_trades(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
    ) -> list[float]:
        """완결된 거래의 수익률 리스트를 추출합니다.

        포지션 전환 기준: position = signals.shift(1).fillna(0)
        - 매수: position이 0→1로 전환되는 시점의 Close
        - 매도: position이 1→0으로 전환되는 시점의 Close
        - 미청산 포지션은 마지막 Close로 강제 청산

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터
        signals : pd.Series
            거래 신호 (0 또는 1)

        Returns
        -------
        list[float]
            거래별 수익률 리스트
        """
        position = signals.shift(1).fillna(0).astype(int)
        pos_diff = position.diff().fillna(0)

        entry_idx = list(df.index[pos_diff > 0])
        exit_idx = list(df.index[pos_diff < 0])

        # 미청산 포지션 처리: 마지막 포지션이 1이면 마지막 날 청산
        if position.iloc[-1] == 1:
            exit_idx.append(df.index[-1])

        trades: list[float] = []
        for entry, exit_ in zip(entry_idx, exit_idx):
            buy = df["Close"].loc[entry]
            sell = df["Close"].loc[exit_]
            trades.append(float(sell / buy - 1))

        return trades
