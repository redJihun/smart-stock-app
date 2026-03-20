"""페이퍼 트레이딩 실행기 모듈."""

from __future__ import annotations

import pandas as pd

from smart_stock.backtesting.cost_model import TradingCost
from smart_stock.backtesting.position_sizer import PositionSizer
from smart_stock.data.feed import DataFeed
from smart_stock.strategies.base_strategy import BaseStrategy
from smart_stock.tracking.logger import SignalLogger, SignalRecord


class PaperTrader:
    """가상 포트폴리오 기반 페이퍼 트레이딩 실행기.

    DataFeed로부터 실시간 캔들을 구독하여 전략 시그널을 생성하고,
    가상 매수/매도를 실행한다. 실제 자본 없이 Go-Live Gate 데이터를 축적한다.

    Parameters
    ----------
    strategy : BaseStrategy
        시그널 생성 전략
    feed : DataFeed
        실시간 데이터 피드
    ticker : str
        종목 코드 (예: "005930") — SignalRecord 기록 용
    initial_capital : float, optional
        초기 자본금 (기본값: 1_000_000.0)
    cost_model : TradingCost | None, optional
        거래 비용 모델 (기본값: None, 비용 미적용)
    position_sizer : PositionSizer | None, optional
        포지션 사이징 전략 (기본값: None, 자본 100% 투입)
    logger : SignalLogger | None, optional
        시그널 기록기 (기본값: None, 기록 미수행)

    Raises
    ------
    ValueError
        initial_capital <= 0인 경우
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        feed: DataFeed,
        ticker: str,
        initial_capital: float = 1_000_000.0,
        cost_model: TradingCost | None = None,
        position_sizer: PositionSizer | None = None,
        logger: SignalLogger | None = None,
    ) -> None:
        if initial_capital <= 0:
            msg = f"initial_capital은 0보다 커야 합니다. 현재: {initial_capital}"
            raise ValueError(msg)
        self._strategy = strategy
        self._feed = feed
        self._ticker = ticker
        self._initial_capital = initial_capital
        self._cost_model = cost_model
        self._position_sizer = position_sizer
        self._logger = logger

        self._cash: float = initial_capital
        self._shares: float = 0.0
        self._entry_price: float | None = None
        self._last_price: float | None = None
        self._history: pd.DataFrame = pd.DataFrame()
        self._prev_signal: int = 0
        self._completed_trade_returns: list[float] = []
        self._started: bool = False

    @property
    def portfolio_value(self) -> float:
        """현재 포트폴리오 가치 (현금 + 보유 주식 평가액)."""
        if self._last_price is None:
            return self._cash
        return self._cash + self._shares * self._last_price

    @property
    def position(self) -> int:
        """현재 포지션. 0=미보유, 1=보유."""
        return 1 if self._shares > 0.0 else 0

    def start(self) -> None:
        """피드 구독을 시작하고 폴링을 시작한다.

        Notes
        -----
        이미 시작된 경우 아무 작업도 하지 않는다 (subscribe 중복 방지).
        """
        if self._started:
            return
        self._feed.subscribe(self._on_candle)
        self._feed.start()
        self._started = True

    def stop(self) -> None:
        """피드 폴링을 중단한다."""
        self._feed.stop()

    def __enter__(self) -> PaperTrader:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.stop()

    def _on_candle(self, df: pd.DataFrame) -> None:
        """새 캔들 수신 시 호출되는 콜백.

        Notes
        -----
        history에 concat 후 중복 제거(keep="last")하여 최신 데이터 우선 유지.
        시그널이 NaN이면 (데이터 부족) 조기 반환한다.
        """
        # 1. history 갱신 (중복 제거: 새 데이터 우선)
        if self._history.empty:
            self._history = df.copy()
        else:
            combined = pd.concat([self._history, df])
            mask = ~combined.index.duplicated(keep="last")
            self._history = combined[mask].sort_index()

        # 2. last_price 갱신
        self._last_price = float(self._history["Close"].iloc[-1])

        # 3. 시그널 생성 (NaN 방어)
        signals = self._strategy.generate_signals(self._history)
        last_val = signals.iloc[-1]
        if pd.isna(last_val):
            return
        curr_signal = int(last_val)

        # 4. 포지션 전환 감지 → 가상 주문
        price = self._last_price
        if self._prev_signal == 0 and curr_signal == 1 and self.position == 0:
            self._execute_buy(price)
        elif self._prev_signal == 1 and curr_signal == 0 and self.position == 1:
            self._execute_sell(price)

        # 5. logger 기록 (시그널 변화 시만)
        if self._logger is not None and curr_signal != self._prev_signal:
            signal_code = 1 if curr_signal == 1 else -1
            record = SignalRecord(
                strategy_name=self._strategy.name,
                ticker=self._ticker,
                signal_date=pd.Timestamp(self._history.index[-1]),
                signal=signal_code,
                price=price,
                logged_at=pd.Timestamp.now(),
            )
            self._logger.log(record)

        # 6. prev_signal 갱신
        self._prev_signal = curr_signal

    def _execute_buy(self, price: float) -> None:
        """가상 매수 실행.

        Notes
        -----
        position_sizer가 없으면 현금 100% 투입.
        sizer가 0.0을 반환하면 (Kelly 데이터 부족 등) 매수 건너뜀.
        """
        fraction = (
            self._position_sizer.calculate(
                self.portfolio_value, self._completed_trade_returns
            )
            if self._position_sizer is not None
            else 1.0
        )
        invest = self._cash * fraction
        if invest <= 0.0:
            return

        if self._cost_model is not None:
            # invest = shares * price * (1 + buy_cost_rate)
            self._shares = invest / (price * (1.0 + self._cost_model.buy_cost_rate()))
        else:
            self._shares = invest / price

        self._cash -= invest
        self._entry_price = price

    def _execute_sell(self, price: float) -> None:
        """가상 매도 실행 (전량 매도).

        Notes
        -----
        trade_return은 비용 전 단순 가격 수익률 (entry_price → price).
        """
        proceeds = self._shares * price

        if self._cost_model is not None:
            net = proceeds * (1.0 - self._cost_model.sell_cost_rate())
        else:
            net = proceeds

        self._cash += net

        if self._entry_price is not None:
            trade_return = price / self._entry_price - 1.0
            self._completed_trade_returns.append(trade_return)

        self._shares = 0.0
        self._entry_price = None
