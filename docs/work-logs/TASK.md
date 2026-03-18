# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-006
### 제목: 백테스트-추적 통합 + 노트북 시각화

### 배경

TASK-004(BacktestEngine)와 TASK-005(SignalLogger/OutcomeTracker)가 독립적으로 완성됐다.
이제 백테스트 실행 시 발생한 매수/매도 이벤트를 SignalLogger에 자동 기록하는
통합 파이프라인을 구현하고, 결과를 시각화하는 노트북을 작성한다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/backtesting/engine.py` — BacktestEngine.run(), BacktestResult 인터페이스
- `src/smart_stock/backtesting/__init__.py` — 현재 퍼블릭 API (수정 대상)
- `src/smart_stock/tracking/logger.py` — SignalLogger, SignalRecord 인터페이스
- `src/smart_stock/strategies/base_strategy.py` — BaseStrategy 타입 확인
- `src/smart_stock/strategies/sma_crossover.py` — generate_signals() 반환값 확인 ({0,1} int)
- `notebooks/01-data-exploration.ipynb` — 노트북 구조 패턴 참고

---

## 구현 명세

> 공통 제약은 `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)

---

### Phase 2: 구현 (3개 Agent — 병렬 가능)

---

#### Agent-구현pipeline → `src/smart_stock/backtesting/pipeline.py` (신규) + `src/smart_stock/backtesting/__init__.py` (수정)

모듈 docstring: `"""백테스트-추적 통합 파이프라인 모듈."""`

**핵심 지식:**
- `generate_signals(df)` 반환값은 `{0, 1}` int Series
  - 0 = 현금 보유, 1 = 롱 포지션
  - 0→1 변화 = 매수 이벤트 (SignalRecord.signal=1)
  - 1→0 변화 = 매도 이벤트 (SignalRecord.signal=-1)
- `signals.diff()` 로 변화 시점 감지

**`pipeline.py` 구현:**

```python
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

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
        if delta == 1.0:   # 0 → 1: 매수
            signal_val = 1
        elif delta == -1.0:  # 1 → 0: 매도
            signal_val = -1
        else:
            continue

        ts = pd.Timestamp(date)  # type: ignore[arg-type]
        price = float(df.loc[ts, "Close"])
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
```

**`__init__.py` 수정** — `run_and_track` 추가 재노출:
```python
from smart_stock.backtesting.engine import BacktestEngine, BacktestResult
from smart_stock.backtesting.metrics import (
    max_drawdown,
    sharpe_ratio,
    total_return,
    win_rate,
)
from smart_stock.backtesting.pipeline import run_and_track

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "max_drawdown",
    "run_and_track",
    "sharpe_ratio",
    "total_return",
    "win_rate",
]
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/backtesting/pipeline.py && uv run mypy src/smart_stock/backtesting/pipeline.py --strict
```

---

#### Agent-구현tests → `tests/test_pipeline.py` (신규)

```python
"""run_and_track 파이프라인 테스트."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from smart_stock.backtesting.engine import BacktestEngine, BacktestResult
from smart_stock.backtesting.pipeline import run_and_track
from smart_stock.tracking.logger import SignalLogger


def _make_df(n: int = 60) -> pd.DataFrame:
    """테스트용 OHLCV DataFrame."""
    idx = pd.date_range("2024-01-02", periods=n, freq="B")
    prices = [100.0 + i for i in range(n)]
    return pd.DataFrame(
        {
            "Open": prices,
            "High": [p + 1 for p in prices],
            "Low": [p - 1 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=idx,
    )


def _make_strategy_mock(signals: pd.Series) -> MagicMock:
    strategy = MagicMock()
    strategy.generate_signals.return_value = signals
    return strategy


class TestRunAndTrackReturn:
    def test_returns_backtest_result(self, tmp_path: Path) -> None:
        """반환값이 BacktestResult 인스턴스여야 함."""
        df = _make_df()
        # 항상 0 시그널 (변화 없음)
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        result = run_and_track(df, strategy, ticker="005930", logger=logger)
        assert isinstance(result, BacktestResult)

    def test_engine_default_created(self, tmp_path: Path) -> None:
        """engine=None 이면 기본 BacktestEngine이 사용됨."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        # engine 파라미터 없이 호출 — 에러 없음
        result = run_and_track(df, strategy, ticker="005930", logger=logger)
        assert result.total_return is not None


class TestRunAndTrackSignalLogging:
    def test_no_signals_logged_when_all_zero(self, tmp_path: Path) -> None:
        """항상 0 시그널이면 기록 없음."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        assert logger.load().empty

    def test_buy_signal_logged(self, tmp_path: Path) -> None:
        """0→1 변화 시점에서 signal=1 레코드가 기록됨."""
        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        logged = logger.load()
        assert len(logged) == 1
        assert int(logged.iloc[0]["signal"]) == 1

    def test_sell_signal_logged(self, tmp_path: Path) -> None:
        """1→0 변화 시점에서 signal=-1 레코드가 기록됨."""
        df = _make_df(n=20)
        vals = [1] * 10 + [0] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="005930", logger=logger)
        logged = logger.load()
        assert len(logged) == 1
        assert int(logged.iloc[0]["signal"]) == -1

    def test_strategy_name_recorded(self, tmp_path: Path) -> None:
        """strategy_name이 클래스명으로 기록됨."""
        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        # 실제 클래스명이 필요하므로 간단 서브클래스 생성
        from smart_stock.strategies.base_strategy import BaseStrategy

        class DummyStrategy(BaseStrategy):
            def generate_signals(self, df: pd.DataFrame) -> pd.Series:
                return signals

        strategy = DummyStrategy()
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="035720", logger=logger)
        logged = logger.load()
        assert logged.iloc[0]["strategy_name"] == "DummyStrategy"

    def test_ticker_recorded(self, tmp_path: Path) -> None:
        """ticker가 기록에 저장됨."""
        df = _make_df(n=20)
        vals = [0] * 10 + [1] * 10
        signals = pd.Series(vals, index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        run_and_track(df, strategy, ticker="AAPL", logger=logger)
        logged = logger.load()
        assert logged.iloc[0]["ticker"] == "AAPL"

    def test_custom_engine_used(self, tmp_path: Path) -> None:
        """주입된 engine이 실제로 사용됨."""
        df = _make_df()
        signals = pd.Series([0] * len(df), index=df.index, dtype=int)
        strategy = _make_strategy_mock(signals)
        logger = SignalLogger(log_dir=tmp_path)
        custom_engine = BacktestEngine(initial_capital=500_000)
        result = run_and_track(
            df, strategy, ticker="005930", engine=custom_engine, logger=logger
        )
        assert isinstance(result, BacktestResult)
```

파일 단위 검증:
```bash
uv run pytest tests/test_pipeline.py -v
```

---

#### Agent-구현notebook → `notebooks/02-backtest-tracking.ipynb` (신규)

노트북 구조 (kebab-case 파일명 규칙 준수):

```
notebooks/02-backtest-tracking.ipynb
```

**셀 구성:**

셀 1 (마크다운):
```markdown
# 02. 백테스트-추적 통합

BacktestEngine + SignalLogger + OutcomeTracker를 run_and_track() 파이프라인으로 연결하는 실습 노트북.
```

셀 2 (코드 — 임포트):
```python
import sys
sys.path.insert(0, '../src')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from smart_stock.data import fetch_stock_cached, Market
from smart_stock.strategies import SMAcrossoverStrategy, RSIStrategy, MACDStrategy
from smart_stock.backtesting import BacktestEngine, run_and_track
from smart_stock.tracking.logger import SignalLogger
from smart_stock.tracking.tracker import OutcomeTracker

plt.rcParams['figure.figsize'] = (14, 5)
plt.rcParams['axes.grid'] = True
```

셀 3 (마크다운): `## 1. 데이터 로드`

셀 4 (코드 — 데이터 로드):
```python
ticker = "005930"
df = fetch_stock_cached(ticker, start="2024-01-01", end="2024-12-31")
print(f"기간: {df.index[0].date()} ~ {df.index[-1].date()}, 거래일: {len(df)}일")
df.tail()
```

셀 5 (마크다운): `## 2. 3개 전략 백테스트 + 시그널 기록`

셀 6 (코드 — 백테스트):
```python
# 임시 logger (tmp_path 대신 기본 경로 사용)
logger = SignalLogger()
logger.clear()  # 이전 기록 초기화

strategies = {
    "SMA(5,20)": SMAcrossoverStrategy(short_window=5, long_window=20),
    "RSI(14)": RSIStrategy(period=14),
    "MACD(12,26,9)": MACDStrategy(),
}

results = {}
for name, strategy in strategies.items():
    engine = BacktestEngine(initial_capital=1_000_000)
    result = run_and_track(df, strategy, ticker=ticker, engine=engine, logger=logger)
    results[name] = result
    print(f"[{name}] 수익률: {result.total_return:.2f}%, MDD: {result.mdd:.2f}%, 샤프: {result.sharpe_ratio:.2f}, 승률: {result.win_rate:.1f}%")
```

셀 7 (마크다운): `## 3. 성과 비교 테이블`

셀 8 (코드 — 성과 테이블):
```python
summary = pd.DataFrame({
    name: {
        "총수익률(%)": round(r.total_return, 2),
        "MDD(%)": round(r.mdd, 2),
        "샤프지수": round(r.sharpe_ratio, 2),
        "승률(%)": round(r.win_rate, 1),
        "거래횟수": r.trade_count,
    }
    for name, r in results.items()
}).T
summary
```

셀 9 (마크다운): `## 4. 포트폴리오 가치 곡선`

셀 10 (코드 — 포트폴리오 시각화):
```python
fig, ax = plt.subplots()
for name, result in results.items():
    ax.plot(result.portfolio.index, result.portfolio.values / 1_000_000, label=name)
ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="원금")
ax.set_title("전략별 포트폴리오 가치 (초기 자본 = 1)")
ax.set_ylabel("포트폴리오 배율")
ax.legend()
plt.tight_layout()
plt.show()
```

셀 11 (마크다운): `## 5. 기록된 시그널 확인`

셀 12 (코드 — 시그널 로그):
```python
signals_df = logger.load()
print(f"총 시그널 수: {len(signals_df)}")
signals_df.head(10)
```

셀 13 (마크다운): `## 6. 매수/매도 시그널 달력 시각화`

셀 14 (코드 — 시그널 마커):
```python
fig, ax = plt.subplots()
ax.plot(df.index, df["Close"], color="steelblue", alpha=0.8, label="종가")

for _, row in signals_df.iterrows():
    if int(row["signal"]) == 1:
        ax.scatter(row["signal_date"], row["price"], marker="^", color="red", s=80, zorder=5)
    elif int(row["signal"]) == -1:
        ax.scatter(row["signal_date"], row["price"], marker="v", color="blue", s=80, zorder=5)

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color="steelblue", label="종가"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="red", markersize=8, label="매수"),
    Line2D([0], [0], marker="v", color="w", markerfacecolor="blue", markersize=8, label="매도"),
]
ax.legend(handles=legend_elements)
ax.set_title(f"{ticker} 매수/매도 시그널 (3개 전략 합산)")
plt.tight_layout()
plt.show()
```

셀 15 (마크다운): `## 7. 결과 추적 (OutcomeTracker)`

셀 16 (코드 — OutcomeTracker):
```python
# 실제 과거 데이터이므로 fetch_stock_cached 재사용
tracker = OutcomeTracker()
outcomes_df = tracker.update(signals_df)
print(f"총 추적 시그널: {len(outcomes_df)}")
outcomes_df[["strategy_name", "ticker", "signal_date", "signal", "entry_price", "outcome_1d", "outcome_1w"]].head(10)
```

파일 단위 검증: Jupyter에서 `Restart & Run All` 에러 없음 확인.

---

### Phase 3: 검증

#### Agent-검증

실행 명령 (순서대로):
```bash
uv run ruff check src/smart_stock/backtesting/pipeline.py
uv run ruff format src/smart_stock/backtesting/pipeline.py
uv run mypy src/smart_stock/backtesting/pipeline.py --strict
uv run pytest tests/test_pipeline.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/backtesting/pipeline.py` 생성
- [ ] `src/smart_stock/backtesting/__init__.py` 수정 (run_and_track 재노출)
- [ ] `tests/test_pipeline.py` 생성 (≥6개 테스트)
- [ ] `notebooks/02-backtest-tracking.ipynb` 생성
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과
- [ ] pytest 전체 테스트 스위트 통과 (기존 96개 + 신규 ≥6개)
- [ ] `RESULT.md` 갱신 완료
