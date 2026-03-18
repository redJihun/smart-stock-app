"""시그널 로깅 모듈."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DEFAULT_TRACKING_DIR = Path("data/tracking")


@dataclass
class SignalRecord:
    """시그널 기록 데이터."""

    strategy_name: str  # 전략 이름 (예: "SMAcrossover")
    ticker: str  # 종목 코드
    signal_date: pd.Timestamp  # 시그널 발생일
    signal: int  # 1=매수, -1=매도, 0=홀드
    price: float  # 시그널 발생일 종가
    logged_at: pd.Timestamp  # 기록 시각


class SignalLogger:
    """시그널 발생 기록을 Parquet 파일에 누적한다."""

    def __init__(self, log_dir: Path = DEFAULT_TRACKING_DIR) -> None:
        self.log_dir = log_dir
        self._path = log_dir / "signals.parquet"

    def log(self, record: SignalRecord) -> None:
        """시그널 1건을 기록한다. (기존 파일 있으면 append)"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        new_row = pd.DataFrame(
            [
                {
                    "strategy_name": record.strategy_name,
                    "ticker": record.ticker,
                    "signal_date": record.signal_date,
                    "signal": record.signal,
                    "price": record.price,
                    "logged_at": record.logged_at,
                }
            ]
        )
        existing = self.load()
        combined = (
            pd.concat([existing, new_row], ignore_index=True)
            if not existing.empty
            else new_row
        )
        combined.to_parquet(self._path)

    def load(self) -> pd.DataFrame:
        """저장된 시그널 전체를 반환한다. 파일이 없으면 빈 DataFrame."""
        if not self._path.exists():
            return pd.DataFrame(
                columns=[
                    "strategy_name",
                    "ticker",
                    "signal_date",
                    "signal",
                    "price",
                    "logged_at",
                ]
            )
        return pd.read_parquet(self._path)

    def clear(self) -> None:
        """저장된 시그널 파일을 삭제한다. (테스트용)"""
        if self._path.exists():
            self._path.unlink()
