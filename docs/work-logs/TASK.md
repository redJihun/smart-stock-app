# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-009
### 제목: 복합 전략 프레임워크 구현 (FR-102)

### 배경

Phase 1 FR-102 요구사항.
현재 각 전략(SMA/RSI/MACD/Bollinger)은 독립적으로 이진 시그널(0/1)을 생성한다.
여러 전략의 시그널을 가중 결합하여 노이즈를 줄이고 다중 지표 기반의 더 강건한 매매 시그널을 만드는 `CompositeStrategy`가 필요하다.

**기존 전략 클래스(BaseStrategy 하위)는 수정하지 않는다.**

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/strategies/base_strategy.py` — BaseStrategy ABC, validate_dataframe
- `src/smart_stock/strategies/sma_crossover.py` — 전략 클래스 참조 패턴
- `src/smart_stock/strategies/__init__.py` — 현재 재노출 목록 (CompositeStrategy 추가 대상)
- `.claude/rules/task-cycle.md` — 공통 코드 제약

---

## 구현 명세

> 공통 제약: `from __future__ import annotations` 첫 줄 / pandas만 사용(numpy 직접 금지, math 허용) / 파일 500줄 이내 / mypy strict / 한국어 docstring (NumPy 스타일)

---

### Phase 2: 구현 (2개 Agent — 병렬 실행 가능)

---

#### Agent-구현composite → `src/smart_stock/strategies/composite.py` (신규) + `src/smart_stock/strategies/__init__.py` (갱신)

**구현할 클래스:**

```python
# src/smart_stock/strategies/composite.py

class CompositeStrategy:
    """여러 전략의 시그널을 가중 결합하는 복합 전략.

    Parameters
    ----------
    strategies : list[tuple[BaseStrategy, float]]
        (전략 인스턴스, 가중치) 쌍의 목록. 가중치는 양수여야 한다.
    threshold : float, optional
        generate_signals()에서 이진 시그널로 변환할 임계값 (기본값: 0.5).
        시그널 강도 >= threshold 이면 1, 미만이면 0.
    name : str, optional
        전략 이름 (기본값: "composite").

    Raises
    ------
    ValueError
        strategies가 비어 있는 경우.
        가중치에 양수가 아닌 값이 포함된 경우.
        threshold가 0~1 범위를 벗어난 경우.
    """

    def generate_signals_strength(self, df: pd.DataFrame) -> pd.Series:
        """연속 시그널 강도를 반환한다 (0.0 ~ 1.0).

        각 전략의 이진 시그널(0/1)을 가중 평균하여 시그널 강도를 계산한다.
        """
        # total_weight = sum(w for _, w in self.strategies)
        # weighted_sum = sum(w * strategy.generate_signals(df).astype(float) for strategy, w in ...)
        # return weighted_sum / total_weight

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """이진 시그널을 반환한다 ({0, 1}).

        generate_signals_strength() >= threshold 이면 1, 미만이면 0.
        """
```

**파라미터 유효성 검증:**
- `strategies`가 빈 리스트이면 `ValueError`
- 가중치에 `<= 0` 값이 있으면 `ValueError`
- `threshold`가 `[0.0, 1.0]` 범위를 벗어나면 `ValueError`

**`__init__.py` 갱신:**
```python
from smart_stock.strategies.composite import CompositeStrategy

# __all__에 "CompositeStrategy" 알파벳순 위치에 추가
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/strategies/composite.py src/smart_stock/strategies/__init__.py
uv run mypy src/smart_stock/strategies/composite.py src/smart_stock/strategies/__init__.py --strict
```

---

#### Agent-구현tests → `tests/test_composite_strategy.py` (신규)

**테스트 구조:**

```python
# 공용 헬퍼: _make_ohlcv(rows=60) — 60일치 OHLCV DataFrame
# Fixtures: sample_df, sma_strategy, rsi_strategy, macd_strategy

class TestCompositeStrategyInit:
    # strategies 빈 리스트 → ValueError
    # 가중치 <= 0 → ValueError
    # threshold 범위 초과 → ValueError
    # 정상 생성 확인

class TestGenerateSignalsStrength:
    # 반환 타입이 pd.Series인지 확인
    # 길이가 입력 df와 동일한지 확인
    # 값이 [0.0, 1.0] 범위인지 확인
    # 단일 전략(가중치 1.0)이면 해당 전략 시그널과 동일한지 확인
    # 모든 전략이 1 시그널이면 강도=1.0인지 확인
    # 모든 전략이 0 시그널이면 강도=0.0인지 확인

class TestGenerateSignals:
    # 반환 타입이 pd.Series인지 확인
    # 반환값이 0 또는 1만 포함하는지 확인 (이진)
    # threshold=0.0이면 항상 1인지 확인
    # threshold=1.0이면 항상 0인지 확인 (모든 전략이 동시에 1이 아닌 경우)
    # 가중치 변경 시 시그널이 달라지는지 확인

class TestCompositeWithRealStrategies:
    # SMA + RSI 결합 — 정상 실행 확인
    # 3개 전략 결합 — 정상 실행 확인
    # 인덱스가 입력 df와 동일한지 확인
```

**기대 테스트 수: 15개 이상**

파일 단위 검증:
```bash
uv run ruff check tests/test_composite_strategy.py
uv run mypy tests/test_composite_strategy.py --strict
```

---

### Phase 3: 검증

#### Agent-검증

```bash
uv run ruff check src/smart_stock/strategies/composite.py src/smart_stock/strategies/__init__.py tests/test_composite_strategy.py
uv run ruff format src/smart_stock/strategies/composite.py src/smart_stock/strategies/__init__.py tests/test_composite_strategy.py
uv run mypy src/smart_stock/strategies/ --strict
uv run pytest tests/test_composite_strategy.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/strategies/composite.py` 신규 생성 (`CompositeStrategy` 클래스)
- [ ] `src/smart_stock/strategies/__init__.py` 갱신 (`CompositeStrategy` 추가)
- [ ] `tests/test_composite_strategy.py` 신규 생성 (15개 이상 테스트)
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과
- [ ] pytest 전체 테스트 스위트 통과 (기존 159개 + 신규)
- [ ] `RESULT.md` 갱신 완료
