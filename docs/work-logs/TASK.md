# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-010
### 제목: 전략 비교 대시보드 노트북 구현 (FR-104)

### 배경

Phase 1 FR-104 요구사항.
FR-101(지표 라이브러리), FR-102(CompositeStrategy), FR-103(분봉 수집)이 모두 완료되어
이를 종합 활용하는 비교 대시보드가 필요하다.
기존 `02-backtest-tracking.ipynb`는 기본 비교만 있으나, 여기서는
5개 전략의 성과 비교 + 기술적 지표 오버레이 + 파라미터 민감도 분석까지 포함한
더 체계적인 분석 노트북을 구현한다.

**소스 코드 수정 없음** — 기존 모듈 재사용만.

---

## 참고 파일 (먼저 읽을 것)

- `notebooks/02-backtest-tracking.ipynb` — 성과 테이블·포트폴리오 곡선·시그널 시각화 패턴
- `src/smart_stock/strategies/__init__.py` — 사용 가능한 전략 클래스 확인
- `src/smart_stock/analysis/__init__.py` — sma, rsi, bollinger_bands 함수 확인
- `src/smart_stock/backtesting/pipeline.py` — run_and_track() 시그니처 확인
- `.claude/rules/task-cycle.md` — 실행자 금지 행동 확인

---

## 구현 명세

> 노트북 작업이므로 ruff/mypy/pytest 대상 아님. 검증은 `jupyter nbconvert --execute` 사용.

---

### Phase 2: 구현 (단일 Agent)

---

#### Agent-구현dashboard → `notebooks/03-strategy-comparison.ipynb` (신규)

**노트북 셀 구성 (~20셀)**:

```
셀-1:  [설정] import + matplotlib rcParams
       import matplotlib.pyplot as plt, matplotlib.ticker as mticker
       plt.rcParams["figure.figsize"] = (14, 5)
       plt.rcParams["axes.grid"] = True
       import warnings; warnings.filterwarnings("ignore")

셀-2:  [파라미터] 상수 정의
       TICKER = "005930"       # 삼성전자
       START = "2023-01-01"
       END = "2024-12-31"
       INITIAL_CAPITAL = 1_000_000

셀-3:  [데이터] fetch_stock_cached() 로드 + 기간/형태 출력
       df = fetch_stock_cached(TICKER, start=START, end=END)
       print(f"기간: {df.index[0].date()} ~ {df.index[-1].date()}, {len(df)}행")

셀-4:  [전략 초기화] 5개 전략 dict 구성
       sma_st = SMAcrossoverStrategy(short_window=5, long_window=20)
       rsi_st = RSIStrategy(period=14)
       macd_st = MACDStrategy()
       bb_st = BollingerBandStrategy()
       composite_st = CompositeStrategy(strategies=[(sma_st, 0.5), (rsi_st, 0.5)])
       strategies = {
           "SMA(5,20)": sma_st,
           "RSI(14)": rsi_st,
           "MACD": macd_st,
           "Bollinger(20,2)": bb_st,
           "Composite(SMA+RSI)": composite_st,
       }

셀-5:  [백테스트] logger.clear() → 전략별 run_and_track() 실행
       logger = SignalLogger(); logger.clear()
       results = {}
       for name, strategy in strategies.items():
           engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)
           result = run_and_track(df, strategy, ticker=TICKER, engine=engine, logger=logger)
           results[name] = result
           print(f"[{name}] 수익률: {result.total_return:.2f}%, MDD: {result.mdd:.2f}%,
                 샤프: {result.sharpe_ratio:.2f}, 승률: {result.win_rate:.1f}%, 거래: {result.trade_count}회")

셀-6:  [성과 테이블] pd.DataFrame 비교표 → display()
       (02-backtest-tracking 패턴 재사용)

셀-7:  [시각화1] 포트폴리오 가치 곡선 비교
       fig, ax = plt.subplots()
       for name, result in results.items():
           ax.plot(result.portfolio.index, result.portfolio / INITIAL_CAPITAL, label=name)
       ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="원금")
       ax.set_title("전략별 포트폴리오 가치 (초기 자본 = 1)")
       ax.set_ylabel("배율")
       ax.legend(loc="upper left")
       plt.tight_layout(); plt.show()

셀-8:  [시각화2] 드로우다운 비교
       drawdown 계산: dd = portfolio / portfolio.cummax() - 1
       모든 전략의 dd를 동일 axes에 plot

셀-9:  [기술적 지표] 종가 + SMA(20) + SMA(60) 오버레이
       from smart_stock.analysis import sma
       sma20 = sma(df["Close"], 20)
       sma60 = sma(df["Close"], 60)
       ax.plot(종가, SMA20, SMA60 각각 색상 구분)

셀-10: [기술적 지표] RSI(14) 서브플롯
       fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
       ax1: 종가, ax2: RSI + 30/70 기준선 (axhline)

셀-11: [기술적 지표] 볼린저 밴드 오버레이
       from smart_stock.analysis import bollinger_bands
       bb = bollinger_bands(df["Close"])
       ax.fill_between(bb.index, bb["lower"], bb["upper"], alpha=0.2, color="gray", label="밴드")
       ax.plot(bb["middle"], label="중간선")
       ax.plot(df["Close"], label="종가")

셀-12: [파라미터 스캔] SMA window 조합 성과 표
       short_windows = [5, 10, 20]
       long_windows = [20, 50, 60]
       scan 결과를 pd.DataFrame으로 구성 (유효 조합: short < long 만)
       display(scan_results)

셀-13: [CompositeStrategy 가중치 민감도]
       가중치 비율 3가지: (0.3, 0.7), (0.5, 0.5), (0.7, 0.3)
       각각 BacktestEngine.run()으로 성과 비교 표

셀-14: [신호 시각화] 최고 샤프비율 전략의 매수/매도 시그널 오버레이
       best_name = max(results, key=lambda n: results[n].sharpe_ratio)
       signals_df = logger.load()
       best_signals = signals_df[signals_df["strategy"] == best_name]
       (02-backtest-tracking.ipynb 셀-13 패턴 재사용)

셀-15: [결론] 마크다운 텍스트 셀
       # 분석 요약
       전략별 강/약점 표 (텍스트)
```

**주의사항**:
- `logger.clear()` 는 셀-5 시작 전에만 1회 호출 — 중복 기록 방지
- `CompositeStrategy` 초기화 시 동일 인스턴스(`sma_st`, `rsi_st`) 재사용 가능
- 파라미터 스캔(셀-12)은 `SignalLogger` 없이 `BacktestEngine.run()` 직접 사용

파일 단위 검증:
```bash
uv run jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.timeout=120 \
  notebooks/03-strategy-comparison.ipynb \
  --output notebooks/03-strategy-comparison.ipynb
```
오류 발생 시 해당 셀 수정 후 재실행.

---

### Phase 3: 검증

#### Agent-검증

```bash
# 노트북 전체 실행 검증 (커널 재시작 후 순서대로 실행)
uv run jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.timeout=120 \
  notebooks/03-strategy-comparison.ipynb \
  --output notebooks/03-strategy-comparison.ipynb
```

성공 기준:
- 오류 없이 전체 셀 실행 완료
- 성과 비교 테이블 출력됨
- 최소 4개 시각화 차트 생성됨

결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] `notebooks/03-strategy-comparison.ipynb` 신규 생성
- [ ] 5개 전략 성과 비교 테이블 출력
- [ ] 포트폴리오 가치 곡선 + 드로우다운 비교 시각화
- [ ] 기술적 지표 오버레이 차트 (SMA, RSI, 볼린저 밴드)
- [ ] SMA 파라미터 스캔 결과 표
- [ ] 노트북 오류 없이 전체 실행 완료
- [ ] `RESULT.md` 갱신 완료
