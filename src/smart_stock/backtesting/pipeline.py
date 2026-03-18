"""백테스트-추적 통합 파이프라인 모듈."""

from __future__ import annotations

import pandas as pd

from smart_stock.backtesting.engine import BacktestEngine, BacktestResult
from smart_stock.strategies.base_strategy import BaseStrategy
from smart_stock.tracking.logger import SignalLogger, SignalRecord


def run_and_track(
    df: pd.DataFrame,
    strategy: BaseStrategy,
    ticker: str,
    engine: BacktestEngine | None = None,
    logger: SignalLogger | None = None,
) -> BacktestResult:
    """백테스트 실행 후 매수/매도 이벤트를 SignalLogger에 기록한다.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV 데이터 (DatetimeIndex, Close 컬럼 필수)
    strategy : BaseStrategy
        백테스트할 전략 인스턴스
    ticker : str
        종목 코드 (시그널 기록용)
    engine : BacktestEngine | None
        백테스트 엔진. None이면 initial_capital=1_000_000 기본값으로 생성
    logger : SignalLogger | None
        시그널 로거. None이면 기본 경로(data/tracking/)로 생성

    Returns
    -------
    BacktestResult
        백테스트 결과 (total_return, mdd, sharpe_ratio, win_rate, portfolio)
    """
    _engine = engine if engine is not None else BacktestEngine()
    _logger = logger if logger is not None else SignalLogger()

    result = _engine.run(df, strategy)

    # 시그널 변화 감지 및 기록
    signals = strategy.generate_signals(df)
    diff = signals.diff()

    strategy_name = type(strategy).__name__

    for date, delta in diff.items():
        if delta == 1.0:  # 0 → 1: 매수
            signal_val = 1
        elif delta == -1.0:  # 1 → 0: 매도
            signal_val = -1
        else:
            continue

        ts = pd.Timestamp(date)  # type: ignore[arg-type]
        price = float(df.loc[ts, "Close"])  # type: ignore[arg-type]
        _logger.log(
            SignalRecord(
                strategy_name=strategy_name,
                ticker=ticker,
                signal_date=ts,
                signal=signal_val,
                price=price,
                logged_at=pd.Timestamp.now(),
            )
        )

    return result
