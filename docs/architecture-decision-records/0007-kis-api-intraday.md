# ADR-0007: 한국 분봉 데이터 소스로 KIS API 선택

| 항목 | 내용 |
|------|------|
| 상태 | Accepted |
| 날짜 | 2026-03-18 |
| 결정자 | @hong |

---

## 맥락 (Context)

Phase 0에서는 일봉(1d) 데이터만 지원했다. PRD 페르소나 B(데이 트레이더)의 대시보드와
단기 전략 지원을 위해 분봉(1m / 5m / 15m / 30m / 1h) 데이터 수집이 필요해졌다.

해외 주식은 `yfinance`가 `interval` 파라미터로 분봉을 이미 지원한다.
문제는 국내 주식이다. 기존에 사용 중인 `FinanceDataReader(fdr)`는 분봉을 지원하지 않는다.

국내 분봉 데이터를 수집할 수 있는 현실적인 선택지를 검토했다.

## 결정 (Decision)

**한국투자증권 KIS Developers Open API**를 채택하여 `kis_client.py` wrapper를 신규 구현한다.

- 엔드포인트: `/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice`
- 인증: OAuth2 client_credentials 방식 (access_token 발급 후 Bearer 헤더)
- 환경변수: `KIS_APP_KEY` / `KIS_APP_SECRET` / `KIS_ACCOUNT_NO` (필수), `KIS_MOCK` (선택)
- 지원 interval: `1m` / `5m` / `10m` / `15m` / `30m` / `1h`
- 반환: 기존 표준 OHLCV DataFrame (DatetimeIndex, `normalize_columns` + `validate_schema` 적용)

`_fetch_kr()`에서 `interval == "1d"`이면 기존 fdr 경로를 유지하고,
`interval != "1d"`이면 `kis_client.fetch_kr_intraday()`를 날짜별 루프로 호출한다.

### 비교 검토한 선택지

| 선택지 | 설명 | 탈락 이유 |
|--------|------|-----------|
| **pykis** (비공식 라이브러리) | KIS API 비공식 Python wrapper | 관리 주체 불명확, 스키마 변경 시 대응 불투명 |
| **OpenDartReader + NAVER 금융 크롤링** | 공시 데이터 + 웹 크롤링 조합 | 크롤링은 서비스 약관 위반 위험, 분봉 미지원 |
| **KRX 공식 API** | 한국거래소 정보데이터시스템 | 실시간·분봉 데이터 미제공, 일별 집계만 제공 |
| **KIS Open API (채택)** | 한투증권 공식 REST API | 무료, 분봉 지원, OAuth2 표준 인증, 공식 문서 충실 |

### 참고자료 (References)

- KIS Developers: `https://apiportal.koreainvestment.com`
- 엔드포인트: `GET /uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice`
- PRD FR-103: 분봉 데이터 수집 기능 요구사항

## 결과 (Consequences)

### 이점 (Benefits)

- 국내 분봉 데이터를 공식 채널에서 무료로 수집 가능
- 기존 `fetch_stock` / `fetch_stock_cached` API를 유지한 채 `interval` 파라미터만 추가 — 하위 호환성 유지
- 모의투자(`KIS_MOCK=true`) / 실거래 서버 전환이 환경변수 하나로 가능
- 표준 OHLCV 스키마로 정규화하여 전략 모듈과의 인터페이스 동일

### 단점 (Drawbacks)

- KIS 계좌 개설 및 앱 등록 필수 (계좌 없는 사용자는 사용 불가)
- access_token 유효기간(24시간)으로 인해 장기 실행 시 토큰 갱신 로직 필요 (현재 미구현)
- 1일치 분봉만 조회 가능 → 범위 조회 시 날짜별 루프 필요, API 호출 횟수 증가

### 리스크 (Risks)

- **Rate Limit**: KIS API는 초당 호출 제한이 있음. 날짜 범위가 길면 429 오류 발생 가능
  - 대응: 호출 간 딜레이 추가 또는 실패한 날짜는 건너뛰는 예외 처리 적용 (`BLE001` 허용)
- **API 스키마 변경**: KIS 응답 필드명(`stck_oprc` 등)이 변경될 경우 파싱 코드 수정 필요
  - 대응: `_parse_response()`를 단일 함수로 격리하여 변경 범위를 최소화
- **환경변수 유출**: `KIS_APP_KEY` 등 민감 정보가 코드에 하드코딩될 위험
  - 대응: `.env` 파일 + `.gitignore` 등록, 환경변수 검증은 런타임에만 수행

## 부록 (Appendix)

### 분봉 조회 흐름

```
fetch_stock(ticker, start, end, interval="5m")
  └─ _fetch_kr(ticker, start_str, end_str, interval="5m")
       └─ [날짜 루프] fetch_kr_intraday(ticker, "YYYYMMDD", interval="5m")
            ├─ _validate_interval()      # "5m" 허용 여부 확인
            ├─ _validate_env_vars()      # 환경변수 존재 확인
            ├─ _get_access_token()       # OAuth2 토큰 발급
            ├─ _fetch_from_kis_api()     # REST GET 호출
            └─ _parse_response()         # → 표준 OHLCV DataFrame
```

### interval 코드 매핑

| interval 파라미터 | KIS `fid_graph_tp_cd` 값 |
|-------------------|--------------------------|
| `1m`              | `"1"`                    |
| `5m`              | `"5"`                    |
| `10m`             | `"10"`                   |
| `15m`             | `"15"`                   |
| `30m`             | `"30"`                   |
| `1h`              | `"60"`                   |

### 필수 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|-----------|------|
| `KIS_APP_KEY` | 필수 | 앱 키 |
| `KIS_APP_SECRET` | 필수 | 앱 시크릿 |
| `KIS_ACCOUNT_NO` | 필수 | 계좌번호 |
| `KIS_ACCOUNT_PROD_CODE` | 선택 (기본 `"01"`) | 계좌 상품 코드 |
| `KIS_MOCK` | 선택 (기본 `""`) | `"true"` 설정 시 모의투자 서버 사용 |
