# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-012
### 제목: 포지션 사이징 구현 (FR-202)

### 배경

Phase 2 FR-202 요구사항.
TASK-011에서 거래 비용 모델(`TradingCost`)을 구현했지만,
현재 `BacktestEngine`은 모든 거래에서 자본 100%를 투입하는 방식만 지원한다.
현실적인 트레이딩에서는 Kelly Criterion, 고정 비율 등 다양한 포지션 사이징 전략을 사용하므로,
`PositionSizer` ABC와 3가지 구현체를 도입하여 `BacktestEngine`에 통합한다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/backtesting/engine.py` — `BacktestEngine._build_portfolio()` 수정 대상
- `src/smart_stock/backtesting/cost_model.py` — 클래스 설계 패턴 참고 (일반 클래스, `__init__` 검증)
- `src/smart_stock/backtesting/__init__.py` — 퍼블릭 API 재노출 현황
- `tests/test_backtesting_engine.py` — backward-compatibility 검증 기준
- `.claude/rules/task-cycle.md` — 실행자 금지 행동 확인

---

## 구현 명세

> 공통 제약: `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)

---

### Phase 2: 구현 (단일 Agent)

---

#### Agent-구현sizer → 4개 파일 수정/신규

---

##### 1. `src/smart_stock/backtesting/position_sizer.py` (신규, ~100줄)

```python
from __future__ import annotations

import math
from abc import ABC, abstractmethod


class PositionSizer(ABC):
    """포지션 사이징 추상 기반 클래스.

    Parameters
    ----------
    (없음 — 서브클래스에서 정의)

    Notes
    -----
    calculate()는 항상 [0.0, 1.0] 범위의 투입 비율(fraction)을 반환해야 한다.
    """

    @abstractmethod
    def calculate(
        self,
        portfolio_value: float,
        trade_returns: list[float],
    ) -> float:
        """투입 비율(fraction)을 계산한다.

        Parameters
        ----------
        portfolio_value : float
            현재 포트폴리오 가치 (단위: 원)
        trade_returns : list[float]
            지금까지 완결된 거래 수익률 리스트 (소수, 예: 0.05 = 5%)

        Returns
        -------
        float
            투입 비율 [0.0, 1.0]
        """
```

**FixedAmountSizer**:
```python
class FixedAmountSizer(PositionSizer):
    """매 거래마다 고정 금액을 투입하는 사이저.

    Parameters
    ----------
    amount : float
        매 거래마다 투입할 고정 금액 (양수여야 함)

    Raises
    ------
    ValueError
        amount <= 0인 경우
    """

    def __init__(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"amount는 0보다 커야 합니다. 현재: {amount}")
        self.amount = amount

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        if portfolio_value <= 0:
            return 0.0
        return min(self.amount / portfolio_value, 1.0)
```

**FixedFractionSizer**:
```python
class FixedFractionSizer(PositionSizer):
    """매 거래마다 포트폴리오의 고정 비율을 투입하는 사이저.

    Parameters
    ----------
    fraction : float
        투입 비율 (0 초과 1 이하)

    Raises
    ------
    ValueError
        fraction <= 0 또는 fraction > 1.0인 경우
    """

    def __init__(self, fraction: float) -> None:
        if fraction <= 0 or fraction > 1.0:
            raise ValueError(f"fraction은 (0, 1] 범위여야 합니다. 현재: {fraction}")
        self.fraction = fraction

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        return self.fraction
```

**KellyCriterionSizer**:
```python
class KellyCriterionSizer(PositionSizer):
    """Kelly Criterion으로 최적 투입 비율을 계산하는 사이저.

    f* = (b * p - q) / b
    b = 평균 이익 / 평균 손실 비율
    p = 승률, q = 1 - p

    Parameters
    ----------
    max_fraction : float, optional
        최대 투입 비율 상한 (기본값: 0.25)
        과레버리지 방지를 위해 f* > max_fraction이면 max_fraction으로 클리핑

    Raises
    ------
    ValueError
        max_fraction <= 0 또는 max_fraction > 1.0인 경우

    Notes
    -----
    과거 거래 데이터가 2개 미만이면 0.0 반환 (통계적 불충분)
    f* < 0 (기대값 음수 전략)이면 0.0으로 클리핑
    """

    def __init__(self, max_fraction: float = 0.25) -> None:
        if max_fraction <= 0 or max_fraction > 1.0:
            raise ValueError(f"max_fraction은 (0, 1] 범위여야 합니다. 현재: {max_fraction}")
        self.max_fraction = max_fraction

    def calculate(self, portfolio_value: float, trade_returns: list[float]) -> float:
        returns = [r for r in trade_returns if r != 0.0]
        if len(returns) < 2:
            return 0.0

        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]

        if not losses:
            return self.max_fraction
        if not wins:
            return 0.0

        p = len(wins) / len(returns)
        q = 1.0 - p
        avg_win = sum(wins) / len(wins)
        avg_loss = abs(sum(losses) / len(losses))
        b = avg_win / avg_loss

        f_star = (b * p - q) / b
        return max(0.0, min(f_star, self.max_fraction))
```

---

##### 2. `src/smart_stock/backtesting/engine.py` (수정)

**import 추가**:
```python
from smart_stock.backtesting.position_sizer import PositionSizer
```

**BacktestEngine.__init__ 수정**:
```python
def __init__(
    self,
    initial_capital: float = 1_000_000.0,
    cost_model: TradingCost | None = None,
    position_sizer: PositionSizer | None = None,  # 신규 파라미터 (마지막에 추가)
) -> None:
    """초기화.

    Parameters
    ----------
    initial_capital : float, optional
        초기 자본금 (기본값: 1,000,000)
    cost_model : TradingCost | None, optional
        거래 비용 모델 (기본값: None, 비용 미적용)
    position_sizer : PositionSizer | None, optional
        포지션 사이징 전략 (기본값: None, 자본 100% 투입)
    ...
    """
    ...
    self.position_sizer = position_sizer
```

**_build_portfolio() 수정** — PositionSizer 분기 추가:

`position_sizer is None`이면 기존 벡터 연산 경로 그대로 유지 (backward-compatible).
`position_sizer`가 있으면 `_compute_sized_position()` private 메서드를 호출하여 fraction Series를 계산한 후, 기존 `position` 대신 사용.

**_compute_sized_position() private 메서드 추가**:

```python
def _compute_sized_position(
    self,
    df: pd.DataFrame,
    signals: pd.Series,
) -> pd.Series:
    """PositionSizer를 적용하여 포지션 비율 시계열을 계산한다.

    거래 진입 시점마다 PositionSizer.calculate()를 호출하여
    해당 거래의 투입 비율을 결정한다.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV 데이터
    signals : pd.Series
        거래 신호 (0 또는 1)

    Returns
    -------
    pd.Series
        포지션 비율 시계열 (0.0~1.0)
    """
    # self.position_sizer가 None이 아님을 이미 호출자에서 검증
    sizer = self.position_sizer
    assert sizer is not None  # mypy를 위한 타입 좁히기

    shifted = signals.shift(1).fillna(0)
    pos_diff = shifted.diff().fillna(0)

    fractions = pd.Series(0.0, index=df.index)
    completed_trade_returns: list[float] = []
    current_fraction = 0.0
    entry_price: float | None = None

    for idx in df.index:
        diff = float(pos_diff.loc[idx])
        if diff > 0:  # 매수 진입
            current_fraction = sizer.calculate(
                self.initial_capital, completed_trade_returns
            )
            entry_price = float(df["Close"].loc[idx])
        elif diff < 0:  # 매도 청산
            if entry_price is not None:
                trade_ret = float(df["Close"].loc[idx]) / entry_price - 1.0
                completed_trade_returns.append(trade_ret)
            current_fraction = 0.0
            entry_price = None
        fractions.loc[idx] = current_fraction

    return fractions
```

**_build_portfolio() 분기 로직**:

```python
def _build_portfolio(self, df, signals) -> tuple[pd.Series, float]:
    if self.position_sizer is not None:
        position = self._compute_sized_position(df, signals)
    else:
        position = signals.shift(1).fillna(0)
    pos_diff = position.diff().fillna(0)
    # 이하 기존 로직 동일 (cost_model 적용 포함)
    ...
```

주의: `pos_diff`를 기반으로 매수/매도 시점을 감지하는 cost_model 로직은 동일하게 동작합니다. PositionSizer 경로에서도 fractions가 0→양수(매수 진입)와 양수→0(매도 청산)으로 변화하므로 `pos_diff > 0`, `pos_diff < 0` 조건이 정상 작동합니다.

---

##### 3. `src/smart_stock/backtesting/__init__.py` (수정)

`PositionSizer` 4개 클래스 추가:
```python
from smart_stock.backtesting.position_sizer import (
    FixedAmountSizer,
    FixedFractionSizer,
    KellyCriterionSizer,
    PositionSizer,
)

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "FixedAmountSizer",
    "FixedFractionSizer",
    "KellyCriterionSizer",
    "KellyCriterionSizer",  # 중복 제거 후 알파벳순 정렬
    "PositionSizer",
    "TradingCost",
    "max_drawdown",
    "run_and_track",
    "sharpe_ratio",
    "total_return",
    "win_rate",
]
```

(실제 작성 시 중복 없이 알파벳순 정렬)

---

##### 4. `tests/test_position_sizer.py` (신규, ~17개 테스트)

```
TestFixedAmountSizer (4개):
- test_normal_fraction_calculation    — amount=500_000, portfolio=1_000_000 → 0.5
- test_clips_to_one_when_amount_exceeds_portfolio — amount > portfolio → 1.0
- test_invalid_amount_raises          — amount <= 0 → ValueError
- test_ignores_trade_returns          — trade_returns에 무관하게 동일 결과

TestFixedFractionSizer (4개):
- test_returns_fixed_fraction         — fraction=0.3 항상 0.3 반환
- test_full_capital_valid             — fraction=1.0 허용
- test_zero_fraction_raises           — fraction=0.0 → ValueError
- test_over_one_raises                — fraction=1.1 → ValueError

TestKellyCriterionSizer (7개):
- test_no_trades_returns_zero         — [] → 0.0
- test_one_trade_returns_zero         — [0.1] (1개) → 0.0
- test_only_wins_returns_max_fraction — 손실 없음 → max_fraction
- test_only_losses_returns_zero       — 이익 없음 → 0.0
- test_negative_f_star_clips_to_zero  — 기대값 음수 전략 → 0.0
- test_exceeds_max_fraction_clips     — f* > 0.25 → 0.25
- test_invalid_max_fraction_raises    — max_fraction=0 또는 1.5 → ValueError

TestPositionSizerIntegration (2개):
- test_engine_with_fixed_fraction_sizer_reduces_portfolio
  — FixedFractionSizer(0.5) 적용 시 100% 투입 대비 변동 확인
- test_engine_none_sizer_backward_compatible
  — position_sizer=None → 기존 동작과 동일 결과
```

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/backtesting/position_sizer.py && uv run mypy src/smart_stock/backtesting/position_sizer.py --strict
```

---

### Phase 3: 검증

#### Agent-검증 (구현 완료 후 동일 Agent가 순서대로 실행)

```bash
uv run ruff check src/smart_stock/backtesting/
uv run ruff format src/smart_stock/backtesting/
uv run mypy src/smart_stock/backtesting/ --strict
uv run pytest tests/test_position_sizer.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/backtesting/position_sizer.py` 신규 생성
- [ ] `BacktestEngine(position_sizer=FixedFractionSizer(0.5))` 동작
- [ ] `BacktestEngine(position_sizer=KellyCriterionSizer())` 동작
- [ ] `position_sizer=None` 시 기존 동작 완전 보존 (회귀 없음)
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과 (~17개)
- [ ] pytest 전체 테스트 스위트 통과 (기존 193개 보존)
- [ ] `RESULT.md` 갱신 완료
