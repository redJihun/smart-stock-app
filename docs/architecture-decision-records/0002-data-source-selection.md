# ADR-0002: 데이터 소스 선택 (FinanceDataReader + yfinance)

| 항목 | 내용 |
|------|------|
| 상태 | Accepted |
| 날짜 | 2026-03-13 |
| 결정자 | 홍지훈 |

---

## 맥락 (Context)

국내외 주식 데이터를 수집해야 한다. 선택 기준은 다음과 같다:

- **무료** 사용 가능
- **범용성** — 다양한 시장·종목 지원, API 호환성 좋음
- **참고 자료** — 커뮤니티 예제, 튜토리얼 풍부
- **유지보수** — 활발히 관리되는 라이브러리
- **데이터 정합성** — 신뢰할 수 있는 데이터 출처
- **조회 속도** — 탐색 단계에서 빠른 피드백

후보 라이브러리:

| 라이브러리 | 출처 | 무료 | 국내 지원 | 자료량 | 유지보수 |
|-----------|------|------|----------|--------|----------|
| FinanceDataReader | KRX 공식 데이터 등 | ✓ | ★★★ | ★★ | 활발 |
| yfinance | Yahoo Finance (비공식) | ✓ | ★ (해외 상장) | ★★★ | 활발 |
| pykrx | KRX 공식 | ✓ | ★★★ | ★ | 보통 |
| KIS API | 한국투자증권 | 부분 유료 | ★★★ | ★★ | 공식 |
| pandas-datareader | 여러 소스 | ✓ | ✗ | ★★★ | 저하 |

## 결정 (Decision)

**FinanceDataReader(fdr)를 국내 주식 메인**, **yfinance를 해외 주식 보조**로 사용하는 조합을 채택한다.

- `FinanceDataReader`: KOSPI, KOSDAQ, KRX 종목 목록, 국내 지수 등 국내 데이터 전담
- `yfinance`: 미국 주식, 글로벌 ETF 등 해외 데이터 보조

이 조합은 국내 주식 분석 커뮤니티에서 가장 일반적으로 사용되는 패턴이며,
두 라이브러리 모두 pandas DataFrame을 반환해 API 호환성이 높다.

### 참고자료 (References)

- [FinanceDataReader GitHub](https://github.com/FinanceData/FinanceDataReader)
- [yfinance GitHub](https://github.com/ranaroussi/yfinance)

## 결과 (Consequences)

### 이점 (Benefits)

- 두 라이브러리 모두 pandas DataFrame 반환 — 일관된 인터페이스
- 국내·해외 시장을 하나의 코드베이스에서 처리 가능
- 참고 예제가 많아 초기 탐색 속도가 빠름
- 완전 무료

### 단점 (Drawbacks)

- yfinance는 Yahoo Finance 비공식 래퍼 — Yahoo 정책 변경 시 중단 가능성 있음
- fdr의 실시간 데이터는 제한적 (일봉 기준 전일까지)
- 두 라이브러리의 컬럼 네이밍이 달라 통합 래퍼 작성 필요

### 리스크 (Risks)

- yfinance API 변경에 의한 데이터 수집 중단 가능성 — 핵심 기능이면 대체 소스 준비 필요
- KIS API 등 공식 소스로 전환 시 기존 코드 수정 범위가 크지 않도록 `src/smart_stock/data/` 아래 추상화 레이어를 두는 것이 좋다
