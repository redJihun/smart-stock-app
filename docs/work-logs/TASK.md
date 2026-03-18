# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-008
### 제목: 기술적 지표 라이브러리 구현 (FR-101)

### 배경

Phase 0에서 SMA / RSI / MACD / Bollinger 계산 로직이 각 전략 클래스 내부에 인라인으로 구현되어 있다.
PRD FR-101은 이 지표들을 **독립 함수**로 분리하여 재사용·조합이 가능하도록 요구한다.
`src/smart_stock/analysis/` 디렉토리는 현재 빈 `__init__.py`만 존재한다.

FR-102(복합 전략), FR-104(비교 대시보드)가 이 라이브러리에 의존하므로 Phase 1 최우선 작업이다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/strategies/rsi_strategy.py` — RSI Wilder's EWM 패턴 참조
- `src/smart_stock/strategies/macd_strategy.py` — EMA 계산 패턴 참조
- `src/smart_stock/strategies/bollinger_strategy.py` — rolling std 패턴 참조
- `src/smart_stock/analysis/__init__.py` — 현재 빈 파일 (교체 대상)
- `.claude/rules/task-cycle.md` — 공통 코드 제약

---

## 구현 명세

> 공통 제약: `from __future__ import annotations` 첫 줄 / pandas만 사용(numpy 직접 금지, math 허용) / 파일 500줄 이내 / mypy strict / 한국어 docstring (NumPy 스타일)

---

### Phase 2: 구현 (2개 Agent — 병렬 실행 가능)

---

#### Agent-구현indicators → `src/smart_stock/analysis/indicators.py` (신규) + `src/smart_stock/analysis/__init__.py` (교체)

**구현할 함수 8개 (지표 11개):**

```python
# ── 추세 (Trend) ──────────────────────────────────────────────────────────
def sma(close: pd.Series, window: int) -> pd.Series:
    """단순 이동평균(SMA)."""
    # close.rolling(window).mean()

def ema(close: pd.Series, span: int) -> pd.Series:
    """지수 이동평균(EMA)."""
    # close.ewm(span=span, adjust=False).mean()

# ── 모멘텀 (Momentum) ─────────────────────────────────────────────────────
def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """RSI (Wilder's Smoothing).
    - diff = close.diff()
    - gain = diff.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    - loss = (-diff.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    - rs = gain / loss (loss=0이면 RSI=100)
    - RSI = 100 - (100 / (1 + rs))
    """

def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD (macd, signal, histogram 컬럼 반환).
    - macd_line = ema(fast) - ema(slow)
    - signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    - histogram = macd_line - signal_line
    """

def stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k: int = 14,
    d: int = 3,
) -> pd.DataFrame:
    """스토캐스틱 오실레이터 (k, d 컬럼 반환).
    - lowest_low = low.rolling(k).min()
    - highest_high = high.rolling(k).max()
    - K = (close - lowest_low) / (highest_high - lowest_low) * 100
    - D = K.rolling(d).mean()
    """

# ── 변동성 (Volatility) ───────────────────────────────────────────────────
def bollinger_bands(
    close: pd.Series,
    window: int = 20,
    std_dev: float = 2.0,
) -> pd.DataFrame:
    """볼린저 밴드 (middle, upper, lower, bandwidth 컬럼 반환).
    - middle = close.rolling(window).mean()
    - std = close.rolling(window).std()
    - upper = middle + std_dev * std
    - lower = middle - std_dev * std
    - bandwidth = (upper - lower) / middle
    """

def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """평균 실제 범위(ATR).
    - tr = max(high-low, |high-prev_close|, |low-prev_close|)
    - ATR = tr.ewm(alpha=1/period, adjust=False).mean()
    """

# ── 거래량 (Volume) ───────────────────────────────────────────────────────
def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """온밸런스 볼륨(OBV).
    - direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    - OBV = (direction * volume).cumsum()
    """
```

**파라미터 유효성 검증 (모든 함수 공통):**
- `window`, `period`, `span`, `k`, `d` ≤ 0 이면 `ValueError` 발생

**`__init__.py` 재노출 목록:**
```python
from smart_stock.analysis.indicators import (
    atr, bollinger_bands, ema, macd, obv, rsi, sma, stochastic,
)
__all__ = ["atr", "bollinger_bands", "ema", "macd", "obv", "rsi", "sma", "stochastic"]
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/analysis/ && uv run mypy src/smart_stock/analysis/ --strict
```

---

#### Agent-구현tests → `tests/test_indicators.py` (신규)

**테스트 구조:**

```python
# Fixtures
def _make_ohlcv(rows: int = 60) -> pd.DataFrame:
    """60일치 OHLCV 샘플 데이터 (충분한 warm-up 확보)."""
    # pd.date_range + 랜덤 없이 단조 증가/진동 값으로 구성

# 테스트 클래스
class TestSMA:          # sma — 반환 타입, 길이, NaN 범위
class TestEMA:          # ema — 반환 타입, 길이
class TestRSI:          # rsi — 범위 [0,100], 0 나누기 안전성
class TestMACD:         # macd — 컬럼명, 길이, histogram = macd - signal
class TestStochastic:   # stochastic — 컬럼명, K 범위 [0,100]
class TestBollingerBands:  # bollinger_bands — 컬럼명, upper >= middle >= lower
class TestATR:          # atr — 양수 값, 길이
class TestOBV:          # obv — 반환 타입, 누적합 성질
class TestValidation:   # 파라미터 ≤ 0 → ValueError (각 함수별 1개)
```

**기대 테스트 수: 20개 이상**

파일 단위 검증:
```bash
uv run ruff check tests/test_indicators.py && uv run mypy tests/test_indicators.py --strict
```

---

### Phase 3: 검증

#### Agent-검증

```bash
uv run ruff check src/smart_stock/analysis/ tests/test_indicators.py
uv run ruff format src/smart_stock/analysis/ tests/test_indicators.py
uv run mypy src/smart_stock/analysis/ --strict
uv run pytest tests/test_indicators.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/analysis/indicators.py` 신규 생성 (8개 함수, 파라미터 검증 포함)
- [ ] `src/smart_stock/analysis/__init__.py` 갱신 (8개 함수 재노출)
- [ ] `tests/test_indicators.py` 신규 생성 (20개 이상 테스트)
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과
- [ ] pytest 전체 테스트 스위트 통과 (기존 114개 + 신규)
- [ ] `RESULT.md` 갱신 완료
