"""시그널 결과 추적 모듈."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from smart_stock.data.cache import fetch_stock_cached
from smart_stock.tracking.logger import DEFAULT_TRACKING_DIR


@dataclass
class OutcomeRecord:
    """시그널 결과 기록 데이터."""

    strategy_name: str
    ticker: str
    signal_date: pd.Timestamp
    signal: int
    entry_price: float
    outcome_1d: float | None  # 1 영업일 후 % 수익률 (데이터 없으면 None)
    outcome_1w: float | None  # 5 영업일 후 % 수익률 (데이터 없으면 None)
    updated_at: pd.Timestamp


class OutcomeTracker:
    """시그널의 실제 결과(1d/1w 후 수익률)를 추적·저장한다.

    Parameters
    ----------
    log_dir : Path
        저장 디렉토리
    fetcher : Callable | None
        주가 조회 함수. None이면 fetch_stock_cached 사용 (테스트 시 mock 주입).
    """

    def __init__(
        self,
        log_dir: Path = DEFAULT_TRACKING_DIR,
        fetcher: Callable[..., pd.DataFrame] | None = None,
    ) -> None:
        self.log_dir = log_dir
        self._path = log_dir / "outcomes.parquet"
        self._fetcher = fetcher if fetcher is not None else fetch_stock_cached

    def update(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        """signals_df 각 행에 대해 1d/1w 결과를 계산하고 outcomes.parquet에 저장한다.

        Parameters
        ----------
        signals_df : pd.DataFrame
            SignalLogger.load()로 얻은 시그널 DataFrame
            (columns: strategy_name, ticker, signal_date, signal, price, logged_at)

        Returns
        -------
        pd.DataFrame
            OutcomeRecord 필드로 구성된 결과 DataFrame
        """
        records = []
        for _, row in signals_df.iterrows():
            ticker: str = str(row["ticker"])
            signal_date: pd.Timestamp = pd.Timestamp(row["signal_date"])
            entry_price: float = float(row["price"])

            # fetcher로 시그널 발생일 이후 데이터 조회
            try:
                price_data = self._fetcher(
                    ticker,
                    start=signal_date,
                )
                # signal_date 이후 데이터만 필터
                future = price_data[price_data.index > signal_date]["Close"]
            except Exception:
                future = pd.Series(dtype=float)

            outcome_1d: float | None = None
            outcome_1w: float | None = None

            if len(future) >= 1:
                outcome_1d = float((future.iloc[0] / entry_price - 1) * 100)
            if len(future) >= 5:
                outcome_1w = float((future.iloc[4] / entry_price - 1) * 100)

            records.append(
                {
                    "strategy_name": row["strategy_name"],
                    "ticker": ticker,
                    "signal_date": signal_date,
                    "signal": int(row["signal"]),
                    "entry_price": entry_price,
                    "outcome_1d": outcome_1d,
                    "outcome_1w": outcome_1w,
                    "updated_at": pd.Timestamp.now(),
                }
            )

        result = pd.DataFrame(records)
        if not result.empty:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            result.to_parquet(self._path)
        return result

    def load(self) -> pd.DataFrame:
        """저장된 결과 전체를 반환한다. 파일이 없으면 빈 DataFrame."""
        if not self._path.exists():
            return pd.DataFrame(
                columns=[
                    "strategy_name",
                    "ticker",
                    "signal_date",
                    "signal",
                    "entry_price",
                    "outcome_1d",
                    "outcome_1w",
                    "updated_at",
                ]
            )
        return pd.read_parquet(self._path)
