# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-011
### 제목: 거래 비용 모델 구현 (FR-201)

### 배경

Phase 2 FR-201 요구사항.
현재 `BacktestEngine`은 수수료·세금·슬리피지를 전혀 반영하지 않아
이론적 수익률과 실제 수익률 사이의 괴리가 크다.
`TradingCost` dataclass를 도입하고 `BacktestEngine`에 선택적으로 적용하여
현실적인 백테스트를 가능하게 한다.

---

## 참고 파일 (먼저 읽을 것)

- `src/smart_stock/backtesting/engine.py` — BacktestEngine._build_portfolio() 수정 대상
- `src/smart_stock/backtesting/__init__.py` — 퍼블릭 API 재노출 현황
- `tests/test_backtesting_engine.py` — 기존 테스트 패턴 확인
- `.claude/rules/task-cycle.md` — 실행자 금지 행동 확인

---

## 구현 명세

> 공통 제약: `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)

---

### Phase 2: 구현 (단일 Agent)

---

#### Agent-구현cost → 4개 파일 수정/신규

---

##### 1. `src/smart_stock/backtesting/cost_model.py` (신규, ~80줄)

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradingCost:
    """거래 비용 모델 (수수료 + 세금 + 슬리피지).

    한국 주식 기본값 기준:
    - commission_rate: 0.00015 (0.015%, 매수/매도 각각 적용)
    - tax_rate: 0.0018 (0.18%, 매도 시에만 적용)
    - slippage_rate: 0.0005 (0.05%, 단방향, 매수/매도 각각)

    Parameters
    ----------
    commission_rate : float, optional
        증권사 수수료율 (기본값: 0.00015)
    tax_rate : float, optional
        증권거래세율 (기본값: 0.0018, 매도 시만)
    slippage_rate : float, optional
        슬리피지율 (기본값: 0.0005, 단방향)

    Raises
    ------
    ValueError
        어떤 비율이라도 음수인 경우
    """
    commission_rate: float = 0.00015
    tax_rate: float = 0.0018
    slippage_rate: float = 0.0005

    def __post_init__(self) -> None:
        for name, val in [
            ("commission_rate", self.commission_rate),
            ("tax_rate", self.tax_rate),
            ("slippage_rate", self.slippage_rate),
        ]:
            if val < 0:
                raise ValueError(f"{name}은 0 이상이어야 합니다. 현재: {val}")

    def buy_cost_rate(self) -> float:
        """매수 시 총 비용율.

        Returns
        -------
        float
            commission_rate + slippage_rate
        """
        return self.commission_rate + self.slippage_rate

    def sell_cost_rate(self) -> float:
        """매도 시 총 비용율.

        Returns
        -------
        float
            commission_rate + tax_rate + slippage_rate
        """
        return self.commission_rate + self.tax_rate + self.slippage_rate
```

---

##### 2. `src/smart_stock/backtesting/engine.py` (수정)

**BacktestResult에 `total_cost` 필드 추가** (기본값 0.0으로 backward-compatible):
```python
@dataclass
class BacktestResult:
    total_return: float
    mdd: float
    sharpe_ratio: float
    trade_count: int
    win_rate: float
    portfolio: pd.Series
    total_cost: float = 0.0   # ← 추가: 총 거래 비용 (초기 자본 대비 금액)
```

**BacktestEngine.__init__ 수정**:
```python
def __init__(
    self,
    initial_capital: float = 1_000_000.0,
    cost_model: TradingCost | None = None,
) -> None:
    if initial_capital <= 0:
        raise ValueError("initial_capital은 0보다 커야 합니다.")
    self.initial_capital = initial_capital
    self.cost_model = cost_model
```

**_build_portfolio() 수정** — `(pd.Series, float)` 튜플 반환으로 변경:
```python
def _build_portfolio(
    self,
    df: pd.DataFrame,
    signals: pd.Series,
) -> tuple[pd.Series, float]:
    """포트폴리오 가치 시계열과 총 비용 금액을 계산합니다.

    Returns
    -------
    tuple[pd.Series, float]
        (일별 포트폴리오 가치, 총 거래 비용 금액)
    """
    position = signals.shift(1).fillna(0)
    pos_diff = position.diff().fillna(0)
    daily_returns = df["Close"].pct_change().fillna(0)
    strategy_returns = position * daily_returns

    total_cost = 0.0
    if self.cost_model is not None:
        import pandas as pd  # 이미 임포트된 경우 그대로 사용
        cost_returns = pd.Series(0.0, index=df.index)
        cost_returns[pos_diff > 0] = -self.cost_model.buy_cost_rate()
        cost_returns[pos_diff < 0] = -self.cost_model.sell_cost_rate()
        strategy_returns = strategy_returns + cost_returns
        # 총 비용 금액 = 비용율 합계 × 초기 자본 (근사값)
        total_cost = float(cost_returns.abs().sum() * self.initial_capital)

    portfolio = self.initial_capital * (1 + strategy_returns).cumprod()
    return portfolio, total_cost
```

**run() 메서드 수정** — _build_portfolio 반환값 언패킹:
```python
def run(self, df: pd.DataFrame, strategy: BaseStrategy) -> BacktestResult:
    signals = strategy.generate_signals(df)
    portfolio, total_cost = self._build_portfolio(df, signals)
    trade_returns = self._extract_trades(df, signals)

    return BacktestResult(
        total_return=total_return(portfolio, self.initial_capital),
        mdd=max_drawdown(portfolio),
        sharpe_ratio=sharpe_ratio(portfolio),
        trade_count=len(trade_returns),
        win_rate=win_rate(trade_returns),
        portfolio=portfolio,
        total_cost=total_cost,
    )
```

**임포트 추가**:
```python
from smart_stock.backtesting.cost_model import TradingCost
```

---

##### 3. `src/smart_stock/backtesting/__init__.py` (수정)

`TradingCost` 추가:
```python
from smart_stock.backtesting.cost_model import TradingCost

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "TradingCost",       # ← 추가
    "max_drawdown",
    "run_and_track",
    "sharpe_ratio",
    "total_return",
    "win_rate",
]
```

---

##### 4. `tests/test_cost_model.py` (신규, ~120줄)

테스트 케이스 (~12개):

```
TestTradingCostInit:
- test_default_values()                    — 기본값 검증 (0.00015, 0.0018, 0.0005)
- test_custom_values()                     — 커스텀 값 설정 확인
- test_negative_commission_raises()        — commission_rate < 0 → ValueError
- test_negative_tax_raises()               — tax_rate < 0 → ValueError
- test_negative_slippage_raises()          — slippage_rate < 0 → ValueError
- test_zero_rates_valid()                  — 모든 비율 0 → 정상 초기화

TestTradingCostRates:
- test_buy_cost_rate()                     — commission + slippage
- test_sell_cost_rate()                    — commission + tax + slippage

TestBacktestEngineWithCost:
- test_cost_model_none_same_as_no_cost()   — cost_model=None 시 기존 포트폴리오와 동일
- test_cost_applied_reduces_portfolio()    — cost_model 적용 시 포트폴리오 < 미적용
- test_zero_cost_equals_no_cost()          — 모든 비율 0인 TradingCost → cost_model=None과 동일
- test_total_cost_positive_with_trades()   — 거래 있으면 total_cost > 0
- test_total_cost_zero_without_trades()    — 거래 없으면 total_cost == 0.0
```

**주의**: `_build_portfolio()`의 반환 타입이 `tuple[pd.Series, float]`로 변경됨.
`test_backtesting_engine.py`에서 이 메서드를 직접 호출하는 테스트가 있으면 수정 필요.
→ `tests/test_backtesting_engine.py` 읽어서 직접 호출 여부 확인 후 필요시 수정.

파일 단위 검증:
```bash
uv run ruff check src/smart_stock/backtesting/ && uv run mypy src/smart_stock/backtesting/ --strict
```

---

### Phase 3: 검증

#### Agent-검증 (구현 완료 후 동일 Agent가 순서대로 실행)

```bash
uv run ruff check src/smart_stock/backtesting/
uv run ruff format src/smart_stock/backtesting/
uv run mypy src/smart_stock/backtesting/ --strict
uv run pytest tests/test_cost_model.py -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `src/smart_stock/backtesting/cost_model.py` 신규 생성
- [ ] `BacktestEngine(cost_model=TradingCost())` 동작
- [ ] 비용 적용 시 포트폴리오 값 < 비용 미적용 포트폴리오 값
- [ ] `cost_model=None` 시 기존 동작 완전 보존 (회귀 없음)
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과
- [ ] pytest 전체 테스트 스위트 통과 (기존 180개 보존)
- [ ] `RESULT.md` 갱신 완료
