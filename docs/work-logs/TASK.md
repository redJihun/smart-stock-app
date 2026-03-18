# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-007
### 제목: 분봉 데이터 수집 인프라 구축 (FR-103)

### 배경

Phase 0에서 일봉(1d) 데이터 수집만 지원했다. 데이 트레이딩(페르소나 B) 지원을 위해
분봉(1m/5m/15m/30m/1h) 수집이 필요하다.

- 해외(yfinance): `yf.download`의 `interval` 파라미터로 이미 지원
- 한국(fdr): 분봉 미지원 → KIS API 신규 wrapper 구현 필요

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/data/loader.py` — fetch_stock, _fetch_kr, _fetch_foreign 현재 구조
- `src/smart_stock/data/cache.py` — cache_path, fetch_stock_cached 현재 구조
- `src/smart_stock/data/__init__.py` — 퍼블릭 API 재노출 현황
- `src/smart_stock/data/schema.py` — normalize_columns, validate_schema
- `tests/test_data_loader.py` — 기존 mock 기반 테스트 패턴 참조
- `.claude/rules/task-cycle.md` — 공통 코드 제약

---

## 구현 명세

> 공통 제약: `from __future__ import annotations` 첫 줄 / pandas만 사용 / 파일 500줄 이내 / mypy strict / 한국어 docstring

---

### Phase 2: 구현 (4개 Agent — fetcher·cache는 순차, kis·tests는 병렬 가능)

---

#### Agent-구현fetcher → `src/smart_stock/data/loader.py` (수정)

`fetch_stock`에 `interval` 파라미터 추가. 일봉은 기존 경로 유지.

```python
# 허용 interval 값 (Literal 타입)
Interval = Literal["1d", "1h", "30m", "15m", "5m", "1m"]

def fetch_stock(
    ticker: str,
    start: DateLike | None = None,
    end: DateLike | None = None,
    *,
    market: Market = Market.KR,
    interval: str = "1d",
) -> pd.DataFrame:
    ...

def _fetch_kr(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    # interval == "1d" → 기존 fdr 경로 유지
    # interval != "1d" → kis_client.fetch_kr_intraday 호출
    ...

def _fetch_foreign(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    # yf.download(..., interval=interval)
    ...
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/data/loader.py && uv run mypy src/smart_stock/data/loader.py --strict
```

---

#### Agent-구현cache → `src/smart_stock/data/cache.py` (수정)

`cache_path`와 `fetch_stock_cached`에 `interval` 추가.

```python
def cache_path(
    ticker: str,
    market: Market,
    start: str,
    end: str,
    interval: str = "1d",
) -> Path:
    # 파일명: {ticker}_{start}_{end}_{interval}.parquet
    # 예: 005930_2024-01-01_2024-12-31_5m.parquet
    ...

def fetch_stock_cached(
    ticker: str,
    start: DateLike | None = None,
    end: DateLike | None = None,
    *,
    market: Market = Market.KR,
    interval: str = "1d",
) -> pd.DataFrame:
    ...
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/data/cache.py && uv run mypy src/smart_stock/data/cache.py --strict
```

---

#### Agent-구현kis → `src/smart_stock/data/kis_client.py` (신규)

KIS API 분봉 조회 wrapper. 환경변수로 인증 정보 관리.

```python
"""한국투자증권 KIS API 분봉 데이터 조회 모듈."""

# 환경변수
# KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_NO, KIS_ACCOUNT_PROD_CODE
# KIS_MOCK (="true" 이면 모의투자 서버 사용)

def fetch_kr_intraday(
    ticker: str,
    date: str,             # "YYYYMMDD"
    interval: str = "5m",  # "1m" | "5m" | "10m" | "15m" | "30m" | "1h"
) -> pd.DataFrame:
    """KIS API로 한국 주식 분봉 데이터 조회.

    Parameters
    ----------
    ticker : str
        종목코드 (예: "005930")
    date : str
        조회 날짜 "YYYYMMDD"
    interval : str
        분봉 단위. "1m" | "5m" | "10m" | "15m" | "30m" | "1h"

    Returns
    -------
    pd.DataFrame
        표준 OHLCV 컬럼 + DatetimeIndex

    Raises
    ------
    EnvironmentError
        KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_NO 환경변수 누락 시
    ValueError
        허용되지 않는 interval 값
    """
    ...
```

- KIS API 엔드포인트: `/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice`
- 인증: access_token 발급 후 Authorization 헤더
- 응답 → normalize_columns → validate_schema 적용

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/data/kis_client.py && uv run mypy src/smart_stock/data/kis_client.py --strict
```

---

#### Agent-구현tests → `tests/test_data_loader.py` (수정) + `tests/test_kis_client.py` (신규)

**test_data_loader.py 추가 테스트 (4개):**
- `test_fetch_stock_kr_intraday_calls_kis`: interval="5m" 시 kis_client 호출 확인 (mock)
- `test_fetch_stock_foreign_interval_passed`: interval이 yf.download에 전달되는지 확인
- `test_cache_path_includes_interval`: cache_path 파일명에 interval 포함 검증
- `test_fetch_stock_cached_interval_default`: interval 기본값 "1d" 동작 확인

**test_kis_client.py 신규:**
- `TestFetchKrIntradayValidation`: 잘못된 interval 값 → ValueError
- `TestFetchKrIntradayMissingEnv`: 환경변수 누락 → EnvironmentError
- `TestFetchKrIntradayResponse`: mock HTTP 응답 → OHLCV DataFrame 변환 검증

파일 단위 검증:
```bash
uv run ruff check tests/test_data_loader.py tests/test_kis_client.py
uv run mypy tests/test_data_loader.py tests/test_kis_client.py --strict
```

---

### Phase 3: 검증

#### Agent-검증

```bash
uv run ruff check src/smart_stock/data/
uv run ruff format src/smart_stock/data/
uv run mypy src/smart_stock/data/ --strict
uv run pytest tests/test_data_loader.py tests/test_kis_client.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [x] `src/smart_stock/data/loader.py` 수정 (interval 파라미터)
- [x] `src/smart_stock/data/cache.py` 수정 (interval 파일명 포함)
- [x] `src/smart_stock/data/kis_client.py` 신규 생성
- [x] `src/smart_stock/data/__init__.py` 수정 (fetch_kr_intraday 재노출)
- [x] `tests/test_data_loader.py` 수정 (interval 관련 테스트 4개 추가)
- [x] `tests/test_kis_client.py` 신규 생성
- [ ] ADR-0007: `docs/architecture-decision-records/0007-kis-api-intraday.md` 작성
- [ ] `docs/architecture-decision-records/README.md` + `docs/README.md` 갱신
- [x] ruff check 통과
- [x] ruff format 적용
- [x] mypy --strict 통과
- [x] pytest 신규 테스트 전체 통과
- [x] pytest 전체 테스트 스위트 통과 (기존 104개 + 신규 → 112 passed)
- [x] `RESULT.md` 갱신 완료

---

## 검수 후 추가 수정 사항 (관리자 검토 발견)

> 관리자(Sonnet) 코드 검수 중 발견된 이슈. 실행자가 아래 3건을 수정한 뒤 검증 재실행.

### Fix-1: 스킵 테스트 활성화 — `tests/test_data_loader.py`

`test_cache_path_includes_interval` (라인 216~223), `test_fetch_stock_cached_interval_default` (라인 226~233) 두 함수가 `pytest.skip`으로 비활성화되어 있다.
`cache.py`에 이미 `interval` 파라미터가 구현되어 있으므로 skip을 제거하고 실제 검증 테스트로 교체한다.

```python
def test_cache_path_includes_interval() -> None:
    """cache_path 파일명에 interval이 포함되는지 검증."""
    from smart_stock.data.cache import cache_path
    path = cache_path("005930", "KR", "2024-01-01", "2024-01-01", "5m")
    assert "5m" in path.name

def test_fetch_stock_cached_interval_default() -> None:
    """fetch_stock_cached의 interval 기본값이 '1d'인지 검증."""
    from smart_stock.data.cache import fetch_stock_cached
    import inspect
    sig = inspect.signature(fetch_stock_cached)
    assert sig.parameters["interval"].default == "1d"
```

### Fix-2: `from __future__ import annotations` 추가 — `src/smart_stock/data/cache.py`

`cache.py` 첫 줄에 `from __future__ import annotations` 누락. 프로젝트 공통 제약(`task-cycle.md`) 위반.

```python
# 파일 최상단에 추가
from __future__ import annotations
```

### Fix-3: 불필요한 noqa 주석 제거 — `src/smart_stock/data/kis_client.py`

44라인: `_validate_interval(interval)  # noqa: F841`

F841은 "할당된 변수 미사용" 경고인데, 여기서는 반환값을 변수에 할당하지 않으므로 이 noqa 코멘트가 부적절하다. 제거한다.

```python
# 수정 전
_validate_interval(interval)  # noqa: F841

# 수정 후
_validate_interval(interval)
```

### 검증 (Fix 완료 후)

```bash
uv run ruff check src/smart_stock/data/ tests/test_data_loader.py
uv run mypy src/smart_stock/data/ --strict
uv run pytest tests/test_data_loader.py -v
uv run pytest tests/ -v
```

기대 결과: **114 passed** (기존 112 + skip 해제 2개), 0 skipped
