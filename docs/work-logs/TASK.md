# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-013
### 제목: 실시간 데이터 피드 구현 (FR-203)

### 배경

Phase 2 FR-203 요구사항.
페이퍼 트레이딩(FR-204)과 실시간 시그널 생성의 전제 조건.
KIS API 분봉 wrapper(TASK-007)가 이미 구현되어 있으므로,
이를 주기적으로 호출하는 폴링 기반 `DataFeed` 프레임워크를 도입한다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/data/__init__.py` — 퍼블릭 API 재노출 현황
- `src/smart_stock/data/kis_client.py` — `fetch_kr_intraday` 시그니처 확인
- `src/smart_stock/backtesting/position_sizer.py` — ABC + `__init__` 검증 패턴 참고
- `tests/test_data_loader.py` — mock 기반 테스트 패턴 참고
- `.claude/rules/task-cycle.md` — 실행자 금지 행동 확인

---

## 구현 명세

> 공통 제약: `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)

---

### Phase 2: 구현 (단일 Agent)

---

#### Agent-구현feed → 3개 파일 수정/신규

---

##### 1. `src/smart_stock/data/feed.py` (신규, ~120줄)

```python
from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass
```

**DataFeed ABC**:
```python
class DataFeed(ABC):
    """실시간 데이터 피드 추상 기반 클래스.

    Notes
    -----
    start() / stop() / subscribe() 인터페이스를 제공한다.
    context manager(__enter__ / __exit__)로 생명주기를 관리할 수 있다.
    """

    @abstractmethod
    def start(self) -> None:
        """피드를 시작한다."""

    @abstractmethod
    def stop(self) -> None:
        """피드를 중단한다."""

    @abstractmethod
    def subscribe(self, callback: Callable[[pd.DataFrame], None]) -> None:
        """새 데이터 도착 시 호출될 콜백을 등록한다.

        Parameters
        ----------
        callback : Callable[[pd.DataFrame], None]
            새 캔들 데이터가 담긴 DataFrame을 인자로 받는 함수
        """

    def __enter__(self) -> DataFeed:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.stop()
```

**PollingDataFeed**:
```python
class PollingDataFeed(DataFeed):
    """폴링 기반 실시간 데이터 피드.

    주기적으로 fetcher를 호출하여 새 캔들 데이터를 구독자에게 전달한다.

    Parameters
    ----------
    ticker : str
        종목 코드 (예: "005930")
    interval : str, optional
        분봉 간격 (기본값: "5m"). "1m" | "5m" | "15m" | "30m" | "1h"
    poll_interval : float, optional
        폴링 주기 (초, 기본값: 60.0)
    fetcher : Callable[..., pd.DataFrame] | None, optional
        데이터 수집 함수 (기본값: None → fetch_kr_intraday 사용)

    Raises
    ------
    ValueError
        poll_interval <= 0인 경우
    """

    def __init__(
        self,
        ticker: str,
        interval: str = "5m",
        poll_interval: float = 60.0,
        fetcher: Callable[..., pd.DataFrame] | None = None,
    ) -> None:
        if poll_interval <= 0:
            raise ValueError(f"poll_interval은 0보다 커야 합니다. 현재: {poll_interval}")
        self._ticker = ticker
        self._interval = interval
        self._poll_interval = poll_interval
        self._fetcher = fetcher
        self._callbacks: list[Callable[[pd.DataFrame], None]] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_ts: pd.Timestamp | None = None

    def subscribe(self, callback: Callable[[pd.DataFrame], None]) -> None:
        self._callbacks.append(callback)

    def start(self) -> None:
        """백그라운드 스레드에서 폴링을 시작한다.

        Notes
        -----
        이미 실행 중이면 아무 작업도 하지 않는다.
        스레드는 daemon=True로 설정되어 메인 프로세스 종료 시 자동 종료된다.
        """
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """폴링을 중단하고 스레드가 종료될 때까지 대기한다.

        Notes
        -----
        최대 5초 대기 후 반환한다.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _poll_loop(self) -> None:
        """백그라운드 스레드에서 실행되는 폴링 루프."""
        while not self._stop_event.is_set():
            self._fetch_and_notify()
            self._stop_event.wait(self._poll_interval)

    def _fetch_and_notify(self) -> None:
        """데이터를 fetch하고 새 캔들이 있으면 구독자에게 전달한다.

        Notes
        -----
        fetch 실패(예외 발생, 빈 데이터) 시 조용히 건너뛴다.
        이전 호출 이후의 새 캔들만 콜백에 전달한다 (중복 방지).
        """
        try:
            today = pd.Timestamp.now().strftime("%Y%m%d")
            actual_fetcher = self._fetcher if self._fetcher is not None else _get_default_fetcher()
            df: pd.DataFrame = actual_fetcher(self._ticker, today, self._interval)
        except Exception:  # noqa: BLE001
            return

        if df.empty:
            return

        new_rows = df if self._last_ts is None else df[df.index > self._last_ts]

        if new_rows.empty:
            return

        self._last_ts = pd.Timestamp(df.index[-1])

        for cb in list(self._callbacks):
            cb(new_rows)


def _get_default_fetcher() -> Callable[..., pd.DataFrame]:
    """기본 fetcher(fetch_kr_intraday)를 지연 임포트하여 반환한다."""
    from smart_stock.data.kis_client import fetch_kr_intraday  # noqa: PLC0415

    return fetch_kr_intraday  # type: ignore[return-value]
```

---

##### 2. `src/smart_stock/data/__init__.py` (수정)

`DataFeed`, `PollingDataFeed` 추가:
```python
from smart_stock.data.feed import DataFeed, PollingDataFeed

__all__ = [
    "DataFeed",
    "Market",
    "PollingDataFeed",
    "STANDARD_COLUMNS",
    "fetch_kr_intraday",
    "fetch_stock",
    "fetch_stock_cached",
    "validate_schema",
]
```

(알파벳순 정렬 유지)

---

##### 3. `tests/test_data_feed.py` (신규, ~12개 테스트)

```
TestPollingDataFeedInit (3개):
- test_default_poll_interval   — poll_interval 기본값 60.0 확인
- test_custom_fetcher_stored   — mock fetcher 주입 후 _fetcher 속성 확인
- test_invalid_poll_interval_raises — poll_interval <= 0 → ValueError

TestPollingDataFeedSubscribe (2개):
- test_subscribe_appends_callback     — subscribe() 후 _callbacks 길이 확인
- test_multiple_callbacks_all_called  — 콜백 2개 등록 → _fetch_and_notify() 후 둘 다 호출 확인

TestPollingDataFeedNewDataDetection (3개):
- test_first_fetch_delivers_all_rows   — _last_ts=None → 전체 df 전달
- test_no_new_rows_skips_callback      — 동일 timestamp 재조회 → 콜백 미호출
- test_only_new_rows_delivered         — 새 캔들만 슬라이스해서 전달

TestPollingDataFeedFetchError (2개):
- test_exception_does_not_crash        — fetcher에서 RuntimeError → _fetch_and_notify 정상 반환
- test_empty_dataframe_skips_callback  — 빈 DataFrame → 콜백 미호출

TestPollingDataFeedLifecycle (2개):
- test_start_stop_no_error             — start() + stop() 예외 없이 완료
- test_context_manager_auto_stop       — with 블록 탈출 시 stop() 자동 호출 확인
```

**테스트 헬퍼 패턴**:
```python
def _make_sample_df(start: str = "2024-01-02 09:30", periods: int = 3) -> pd.DataFrame:
    idx = pd.date_range(start, periods=periods, freq="5min")
    return pd.DataFrame(
        {"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.5, "Volume": 10000},
        index=idx,
    )
```

`_fetch_and_notify()`를 직접 호출하는 방식으로 스레드 타이밍 의존성을 없애고 단위 테스트를 안정적으로 유지할 것.

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/data/feed.py && uv run mypy src/smart_stock/data/feed.py --strict
```

---

### Phase 3: 검증

#### Agent-검증 (구현 완료 후 동일 Agent가 순서대로 실행)

```bash
uv run ruff check src/smart_stock/data/
uv run ruff format src/smart_stock/data/
uv run mypy src/smart_stock/data/ --strict
uv run pytest tests/test_data_feed.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/data/feed.py` 신규 생성
- [ ] `DataFeed`, `PollingDataFeed` 퍼블릭 API 재노출
- [ ] `PollingDataFeed(fetcher=mock)._fetch_and_notify()` → 콜백 호출 동작
- [ ] 새 캔들만 슬라이스하여 중복 전달 방지
- [ ] fetch 예외 시 크래시 없이 건너뜀
- [ ] context manager(`with` 블록) 동작
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과 (~12개)
- [ ] pytest 전체 테스트 스위트 통과 (기존 210개 보존)
- [ ] `RESULT.md` 갱신 완료
