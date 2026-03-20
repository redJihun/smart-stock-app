# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-015
### 제목: 웹 대시보드 구현 (FR-206)

### 배경

FR-204(페이퍼 트레이딩)가 완료되어 SignalLogger가 시그널을 Parquet 파일에 기록하고 있다.
FR-206은 이 데이터를 Streamlit 기반 웹 대시보드로 시각화하여,
페르소나 B(트레이더)와 D(UI 개발자)가 성과를 모니터링할 수 있는 환경을 제공한다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/tracking/logger.py` — SignalRecord 필드, 저장 경로 (`data/tracking/signals.parquet`)
- `src/smart_stock/tracking/tracker.py` — OutcomeRecord 필드, 저장 경로 (`data/tracking/outcomes.parquet`)
- `pyproject.toml` — 의존성 추가 위치 확인 (`[project] dependencies` 섹션)
- `.claude/rules/task-cycle.md` — 실행자 금지 행동 확인

---

## 구현 명세

> 공통 제약: `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)
> **핵심 원칙**: `data.py`(순수 함수, mypy strict + pytest 대상) / `app.py`(Streamlit, mypy 적용 제외) 분리

---

### Phase 2: 구현 (단일 Agent)

---

#### Agent-구현dashboard → 5개 파일 신규/수정

---

##### 1. `pyproject.toml` (수정)

`[project] dependencies` 섹션에 추가:
```toml
"streamlit>=1.32",
```

---

##### 2. `src/smart_stock/dashboard/__init__.py` (신규)

```python
"""웹 대시보드 모듈."""

from smart_stock.dashboard.data import (
    DashboardMetrics,
    compute_metrics,
    compute_strategy_summary,
    load_outcomes,
    load_signals,
)

__all__ = [
    "DashboardMetrics",
    "compute_metrics",
    "compute_strategy_summary",
    "load_outcomes",
    "load_signals",
]
```

---

##### 3. `src/smart_stock/dashboard/data.py` (신규, ~130줄)

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
```

**DEFAULT_LOG_DIR**:
```python
DEFAULT_LOG_DIR = Path("data/tracking")
```

**load_signals**:
```python
def load_signals(log_dir: Path = DEFAULT_LOG_DIR) -> pd.DataFrame:
    """signals.parquet 로드.

    Parameters
    ----------
    log_dir : Path
        데이터 디렉토리 (기본값: data/tracking)

    Returns
    -------
    pd.DataFrame
        시그널 데이터. 파일 없으면 빈 DataFrame.
    """
    path = log_dir / "signals.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)
```

**load_outcomes**:
```python
def load_outcomes(log_dir: Path = DEFAULT_LOG_DIR) -> pd.DataFrame:
    """outcomes.parquet 로드.

    Parameters
    ----------
    log_dir : Path
        데이터 디렉토리 (기본값: data/tracking)

    Returns
    -------
    pd.DataFrame
        결과 데이터. 파일 없으면 빈 DataFrame.
    """
    path = log_dir / "outcomes.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)
```

**DashboardMetrics**:
```python
@dataclass
class DashboardMetrics:
    """대시보드 요약 지표.

    Attributes
    ----------
    total_signals : int
        총 시그널 수
    win_rate_1d : float | None
        1일 적중률 (outcome_1d > 0 비율). 데이터 없으면 None.
    win_rate_1w : float | None
        1주 적중률. 데이터 없으면 None.
    avg_return_1d : float | None
        1일 평균 수익률. 데이터 없으면 None.
    avg_return_1w : float | None
        1주 평균 수익률. 데이터 없으면 None.
    """

    total_signals: int
    win_rate_1d: float | None
    win_rate_1w: float | None
    avg_return_1d: float | None
    avg_return_1w: float | None
```

**compute_metrics**:
```python
def compute_metrics(outcomes_df: pd.DataFrame) -> DashboardMetrics:
    """outcomes DataFrame → DashboardMetrics.

    Notes
    -----
    outcomes_df가 비었으면 total_signals=0, 나머지 None 반환.
    매수 시그널(signal == 1)만 집계.
    적중률: outcome_Xd > 0 인 비율 (방향 예측 정확도).
    """
    if outcomes_df.empty:
        return DashboardMetrics(
            total_signals=0,
            win_rate_1d=None,
            win_rate_1w=None,
            avg_return_1d=None,
            avg_return_1w=None,
        )

    total = len(outcomes_df)

    # 1d 지표
    col_1d = "outcome_1d"
    win_rate_1d: float | None = None
    avg_return_1d: float | None = None
    if col_1d in outcomes_df.columns:
        valid_1d = outcomes_df[col_1d].dropna()
        if len(valid_1d) > 0:
            win_rate_1d = float((valid_1d > 0).mean())
            avg_return_1d = float(valid_1d.mean())

    # 1w 지표
    col_1w = "outcome_1w"
    win_rate_1w: float | None = None
    avg_return_1w: float | None = None
    if col_1w in outcomes_df.columns:
        valid_1w = outcomes_df[col_1w].dropna()
        if len(valid_1w) > 0:
            win_rate_1w = float((valid_1w > 0).mean())
            avg_return_1w = float(valid_1w.mean())

    return DashboardMetrics(
        total_signals=total,
        win_rate_1d=win_rate_1d,
        win_rate_1w=win_rate_1w,
        avg_return_1d=avg_return_1d,
        avg_return_1w=avg_return_1w,
    )
```

**compute_strategy_summary**:
```python
def compute_strategy_summary(outcomes_df: pd.DataFrame) -> pd.DataFrame:
    """전략별 집계 DataFrame 반환.

    Returns
    -------
    pd.DataFrame
        컬럼: strategy_name, signal_count, win_rate_1d, avg_return_1d
        빈 outcomes_df이면 빈 DataFrame 반환.

    Notes
    -----
    outcome_1d 컬럼이 없거나 전부 NaN이면 win_rate_1d / avg_return_1d는 NaN.
    """
    if outcomes_df.empty or "strategy_name" not in outcomes_df.columns:
        return pd.DataFrame()

    # outcome_1d 컬럼 없으면 NaN 컬럼 추가
    if "outcome_1d" not in outcomes_df.columns:
        outcomes_df = outcomes_df.copy()
        outcomes_df["outcome_1d"] = float("nan")

    summary = (
        outcomes_df.groupby("strategy_name")
        .agg(
            signal_count=("strategy_name", "count"),
            win_rate_1d=("outcome_1d", lambda s: float((s.dropna() > 0).mean()) if s.dropna().empty is False else float("nan")),
            avg_return_1d=("outcome_1d", lambda s: float(s.dropna().mean()) if s.dropna().empty is False else float("nan")),
        )
        .reset_index()
    )
    return summary
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/dashboard/data.py && uv run mypy src/smart_stock/dashboard/data.py --strict
```

---

##### 4. `src/smart_stock/dashboard/app.py` (신규, ~160줄)

> **주의**: mypy strict 적용 제외 (Streamlit 타입 한계). ruff check/format은 적용.

```python
"""Smart Stock 웹 대시보드."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from smart_stock.dashboard.data import (
    compute_metrics,
    compute_strategy_summary,
    load_outcomes,
    load_signals,
)

_LOG_DIR = Path("data/tracking")


def _fmt_pct(value: float | None) -> str:
    """float | None → 퍼센트 문자열 포맷."""
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def _fmt_ret(value: float | None) -> str:
    """float | None → 수익률 문자열 포맷."""
    if value is None:
        return "—"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def main() -> None:
    """대시보드 메인 함수."""
    st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")
    st.title("Smart Stock Dashboard")

    # 새로고침 버튼
    col_btn, col_path = st.columns([1, 4])
    with col_btn:
        st.button("새로고침")
    with col_path:
        st.caption(f"데이터 경로: {_LOG_DIR.resolve()}")

    st.divider()

    # 데이터 로드
    signals_df = load_signals(_LOG_DIR)
    outcomes_df = load_outcomes(_LOG_DIR)
    metrics = compute_metrics(outcomes_df)

    # ── 요약 지표 4열 ──────────────────────────────────
    st.subheader("요약")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 시그널 수", metrics.total_signals)
    c2.metric("1일 적중률", _fmt_pct(metrics.win_rate_1d))
    c3.metric("1일 평균 수익률", _fmt_ret(metrics.avg_return_1d))
    c4.metric("1주 평균 수익률", _fmt_ret(metrics.avg_return_1w))

    st.divider()

    # ── 시그널 이력 ────────────────────────────────────
    st.subheader("최근 시그널")
    if signals_df.empty:
        st.info("기록된 시그널이 없습니다. PaperTrader를 실행하여 데이터를 축적하세요.")
    else:
        display_df = signals_df.tail(20).iloc[::-1].copy()
        display_df["signal"] = display_df["signal"].map({1: "매수", -1: "매도", 0: "홀드"})
        st.dataframe(
            display_df,
            column_config={
                "strategy_name": st.column_config.TextColumn("전략"),
                "ticker": st.column_config.TextColumn("종목"),
                "signal_date": st.column_config.DatetimeColumn("시그널 시각"),
                "signal": st.column_config.TextColumn("시그널"),
                "price": st.column_config.NumberColumn("가격", format="₩%.0f"),
                "logged_at": st.column_config.DatetimeColumn("기록 시각"),
            },
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── 전략별 성과 ────────────────────────────────────
    st.subheader("전략별 성과")
    if outcomes_df.empty:
        st.info("결과 데이터가 없습니다. OutcomeTracker.update()를 실행하세요.")
    else:
        summary_df = compute_strategy_summary(outcomes_df)
        if summary_df.empty:
            st.info("집계할 데이터가 없습니다.")
        else:
            st.dataframe(
                summary_df,
                column_config={
                    "strategy_name": st.column_config.TextColumn("전략"),
                    "signal_count": st.column_config.NumberColumn("시그널 수"),
                    "win_rate_1d": st.column_config.NumberColumn("1일 적중률", format="%.1f%%"),
                    "avg_return_1d": st.column_config.NumberColumn("1일 평균 수익률", format="%.2f%%"),
                },
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
```

> **실행**: `uv run streamlit run src/smart_stock/dashboard/app.py`

---

##### 5. `tests/test_dashboard_data.py` (신규, 10개 테스트)

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from smart_stock.dashboard.data import (
    DashboardMetrics,
    compute_metrics,
    compute_strategy_summary,
    load_outcomes,
    load_signals,
)
```

**테스트 헬퍼**:
```python
def _make_signals_df() -> pd.DataFrame:
    return pd.DataFrame({
        "strategy_name": ["SMA", "SMA"],
        "ticker": ["005930", "005930"],
        "signal_date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "signal": [1, -1],
        "price": [70000.0, 72000.0],
        "logged_at": pd.to_datetime(["2024-01-02", "2024-01-03"]),
    })


def _make_outcomes_df(
    outcome_1d: list[float | None] | None = None,
    outcome_1w: list[float | None] | None = None,
) -> pd.DataFrame:
    n = 3
    o1d = outcome_1d if outcome_1d is not None else [0.01, -0.005, 0.02]
    o1w = outcome_1w if outcome_1w is not None else [0.02, -0.01, 0.03]
    return pd.DataFrame({
        "strategy_name": ["SMA", "SMA", "RSI"],
        "ticker": ["005930", "005930", "035720"],
        "signal_date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
        "signal": [1, 1, 1],
        "entry_price": [70000.0, 71000.0, 50000.0],
        "outcome_1d": o1d,
        "outcome_1w": o1w,
        "updated_at": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
    })
```

**테스트 클래스**:
```
TestLoadSignals (2개):
- test_load_signals_missing_file
  tmp_path에 파일 없음 → 빈 DataFrame

- test_load_signals_returns_dataframe
  tmp_path에 signals parquet 저장 → 동일 데이터 반환

TestLoadOutcomes (2개):
- test_load_outcomes_missing_file
  tmp_path에 파일 없음 → 빈 DataFrame

- test_load_outcomes_returns_dataframe
  tmp_path에 outcomes parquet 저장 → 동일 데이터 반환

TestComputeMetrics (4개):
- test_metrics_empty_df
  빈 df → DashboardMetrics(total_signals=0, 나머지 None)

- test_metrics_win_rate_1d
  outcome_1d=[0.01, -0.005, 0.02] → win_rate_1d == 2/3

- test_metrics_avg_return_1d
  outcome_1d=[0.01, -0.005, 0.02] → avg_return_1d ≈ (0.01-0.005+0.02)/3

- test_metrics_no_1d_data
  outcome_1d 컬럼 없는 df → win_rate_1d=None, avg_return_1d=None

TestComputeStrategySummary (2개):
- test_summary_empty_df
  빈 df → 빈 DataFrame

- test_summary_groups_by_strategy
  전략 2개("SMA" 2건, "RSI" 1건) → 행 2개, signal_count 검증
```

---

### Phase 3: 검증

#### Agent-검증 (구현 완료 후 동일 Agent가 순서대로 실행)

```bash
uv run ruff check src/smart_stock/dashboard/
uv run ruff format src/smart_stock/dashboard/
uv run mypy src/smart_stock/dashboard/data.py --strict
uv run pytest tests/test_dashboard_data.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/dashboard/__init__.py` 신규 생성
- [ ] `src/smart_stock/dashboard/data.py` 신규 생성
- [ ] `src/smart_stock/dashboard/app.py` 신규 생성
- [ ] `pyproject.toml` streamlit 의존성 추가
- [ ] `load_signals` / `load_outcomes` — 파일 없을 때 빈 DataFrame 반환
- [ ] `compute_metrics` — 빈 df 방어, 적중률·평균 수익률 계산
- [ ] `compute_strategy_summary` — 전략별 집계 (strategy_name, signal_count, win_rate_1d, avg_return_1d)
- [ ] Streamlit 앱 4개 섹션 (요약/시그널이력/전략성과/빈화면안내)
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy `data.py` --strict 통과
- [ ] pytest 신규 테스트 전체 통과 (10개)
- [ ] pytest 전체 테스트 스위트 통과 (기존 237개 보존)
- [ ] `RESULT.md` 갱신 완료
