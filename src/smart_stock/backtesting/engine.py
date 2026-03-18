"""백테스팅 엔진 모듈."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from smart_stock.backtesting.metrics import (
    max_drawdown,
    sharpe_ratio,
    total_return,
    win_rate,
)
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
    """

    total_return: float
    mdd: float
    sharpe_ratio: float
    trade_count: int
    win_rate: float
    portfolio: pd.Series


class BacktestEngine:
    """백테스팅 엔진."""

    def __init__(self, initial_capital: float = 1_000_000.0) -> None:
        """초기화.

        Parameters
        ----------
        initial_capital : float, optional
            초기 자본금 (기본값: 1,000,000)

        Raises
        ------
        ValueError
            initial_capital이 0 이하인 경우
        """
        if initial_capital <= 0:
            raise ValueError("initial_capital은 0보다 커야 합니다.")
        self.initial_capital = initial_capital

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
        portfolio = self._build_portfolio(df, signals)
        trade_returns = self._extract_trades(df, signals)

        return BacktestResult(
            total_return=total_return(portfolio, self.initial_capital),
            mdd=max_drawdown(portfolio),
            sharpe_ratio=sharpe_ratio(portfolio),
            trade_count=len(trade_returns),
            win_rate=win_rate(trade_returns),
            portfolio=portfolio,
        )

    def _build_portfolio(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
    ) -> pd.Series:
        """포트폴리오 가치 시계열을 계산합니다.

        look-ahead bias를 방지하기 위해 시그널을 1일 지연(shift(1))해 적용합니다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터
        signals : pd.Series
            거래 신호 (0 또는 1)

        Returns
        -------
        pd.Series
            일별 포트폴리오 가치
        """
        position = signals.shift(1).fillna(0)
        daily_returns = df["Close"].pct_change().fillna(0)
        strategy_returns = position * daily_returns
        return self.initial_capital * (1 + strategy_returns).cumprod()

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
