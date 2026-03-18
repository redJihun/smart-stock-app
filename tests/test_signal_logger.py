"""SignalLogger 테스트."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from smart_stock.tracking.logger import SignalLogger, SignalRecord


def _make_record(
    strategy: str = "TestStrategy",
    ticker: str = "005930",
    signal: int = 1,
) -> SignalRecord:
    return SignalRecord(
        strategy_name=strategy,
        ticker=ticker,
        signal_date=pd.Timestamp("2024-01-10"),
        signal=signal,
        price=70000.0,
        logged_at=pd.Timestamp("2024-01-10 09:00"),
    )


class TestSignalLoggerLoad:
    def test_load_empty_before_log(self, tmp_path: Path) -> None:
        """파일 없으면 빈 DataFrame 반환."""
        logger = SignalLogger(log_dir=tmp_path)
        df = logger.load()
        assert df.empty

    def test_load_has_expected_columns(self, tmp_path: Path) -> None:
        """빈 DataFrame에도 컬럼이 정의돼 있어야 함."""
        logger = SignalLogger(log_dir=tmp_path)
        df = logger.load()
        assert "strategy_name" in df.columns
        assert "ticker" in df.columns
        assert "signal" in df.columns


class TestSignalLoggerLog:
    def test_log_creates_file(self, tmp_path: Path) -> None:
        """최초 log() 호출 시 parquet 파일 생성."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.log(_make_record())
        assert (tmp_path / "signals.parquet").exists()

    def test_log_appends(self, tmp_path: Path) -> None:
        """두 번 log() 하면 2개 레코드."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.log(_make_record())
        logger.log(_make_record())
        assert len(logger.load()) == 2

    def test_signal_fields_preserved(self, tmp_path: Path) -> None:
        """strategy_name, ticker, signal 등 필드가 보존됨."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.log(_make_record(strategy="SMAcrossover", ticker="035720", signal=1))
        df = logger.load()
        assert df.iloc[0]["strategy_name"] == "SMAcrossover"
        assert df.iloc[0]["ticker"] == "035720"
        assert int(df.iloc[0]["signal"]) == 1

    def test_log_dir_created_automatically(self, tmp_path: Path) -> None:
        """log_dir이 없어도 자동 생성됨."""
        new_dir = tmp_path / "subdir" / "tracking"
        logger = SignalLogger(log_dir=new_dir)
        logger.log(_make_record())
        assert new_dir.exists()

    def test_multiple_strategies(self, tmp_path: Path) -> None:
        """다른 전략명으로 기록하면 두 행 모두 조회 가능."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.log(_make_record(strategy="StratA"))
        logger.log(_make_record(strategy="StratB"))
        df = logger.load()
        assert set(df["strategy_name"]) == {"StratA", "StratB"}


class TestSignalLoggerClear:
    def test_clear_removes_file(self, tmp_path: Path) -> None:
        """clear() 후 파일이 없음."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.log(_make_record())
        logger.clear()
        assert not (tmp_path / "signals.parquet").exists()

    def test_clear_idempotent(self, tmp_path: Path) -> None:
        """파일 없는 상태에서 clear() 해도 에러 없음."""
        logger = SignalLogger(log_dir=tmp_path)
        logger.clear()  # 파일 없는 상태에서 호출
