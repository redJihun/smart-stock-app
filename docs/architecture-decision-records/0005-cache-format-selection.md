# ADR-0005: 로컬 캐시 포맷 선택 (Parquet vs CSV)

| 항목 | 내용 |
|------|------|
| 상태 | Accepted |
| 날짜 | 2026-03-13 |
| 결정자 | 홍지훈 |

---

## 맥락 (Context)

데이터 탐색 및 반복 개발 시 fdr/yfinance 네트워크 호출을 줄이기 위해 로컬 파일 캐싱이 필요하다.
선택 기준:

- **용량 효율성** — 저장 용량과 트래픽
- **I/O 속도** — 로드·저장 성능
- **호환성** — pandas와의 통합 난이도
- **유지보수** — 추가 의존성 최소화
- **인간가독성** — 캐시 파일 직접 확인 가능성

후보 포맷:

| 포맷 | 용량 | 속도 | 가독성 | 의존성 | 비고 |
|------|------|------|--------|--------|------|
| **Parquet** | ★★★ 우수 | ★★★ 우수 | ✗ 이진 | pyarrow | 현대적, 압축 기본 |
| **CSV** | ★ 큼 | ★ 느림 | ✓ 텍스트 | 없음 | 범용, 간단 |
| **HDF5** | ★★ 중간 | ★★ 중간 | ✗ 이진 | tables | 복잡한 데이터 구조용 |
| **Pickle** | ★★ 중간 | ★★★ 우수 | ✗ 이진 | 없음 | 보안 위험 (untrust data) |

## 결정 (Decision)

**Parquet 포맷을 캐시 기본 포맷으로 채택한다.**

- `src/smart_stock/data/cache.py`에서 `DataFrame.to_parquet()` / `pd.read_parquet()` 사용
- 의존성: `pyarrow>=14.0` (필수), 또는 `fastparquet>=1.0` (선택)
- 캐시 경로: `data/raw/{MARKET}_{TICKER}_{START}_{END}.parquet`

**선택 사유:**

1. **용량 효율성** — CSV 대비 50~70% 더 작음. 1년 일봉 데이터 ~50KB (CSV라면 150KB+)
2. **속도** — 로드/저장 모두 CSV 대비 5~10배 빠름. 탐색 반복 시 중요
3. **pandas 기본 지원** — `pd.read_parquet()` 내장. 추가 래퍼 불필요
4. **압축 기본** — 자동 압축으로 스토리지 절감
5. **산업 표준** — 데이터 파이프라인, 분석 도구에서 광범위 지원

## 결과 (Consequences)

### 이점 (Benefits)

- 네트워크 호출 감소로 탐색 개발 속도 향상
- 용량 효율성으로 `data/raw/` 디스크 사용량 최소화
- 테스트 시 임시 Parquet 파일로 I/O 성능 확인 가능
- pyarrow는 가벼운 의존성 (numpy, pandas 이미 필요)

### 단점 (Drawbacks)

- `pyarrow` 또는 `fastparquet` 필수 의존성 추가 필요
- Parquet 파일을 직접 열어 확인 불가능 (pandas 필수)
- 기존 텍스트 기반 도구(grep, head 등)로 검사 불가

### 리스크 (Risks)

- **pyarrow 미설치**: `ImportError` 발생 시 사용자 혼동 가능 — 설치 가이드 명확히
- **호환성**: pandas-pyarrow 버전 호환성 이슈 드물지만, `pyarrow>=14.0` 지정으로 완화
- **마이그레이션**: 향후 포맷 변경 필요 시(예: HDF5, Parquet v2) 기존 캐시 무효화 필요

## 부록 (Appendix)

### 캐시 파일 예시

```
data/raw/
├── KR_005930_20240101_20241231.parquet     (삼성전자, 2024년)
├── US_AAPL_20240101_20241231.parquet       (Apple, 2024년)
└── GLOBAL_7203.T_20240101_20241231.parquet (Toyota, 2024년)
```

### Parquet vs CSV 성능 비교 (1년 일봉 기준)

```python
import pandas as pd
import time

# 샘플 데이터: 252행 × 5열
df = pd.DataFrame({
    'Open': [100.0] * 252,
    'High': [110.0] * 252,
    'Low': [90.0] * 252,
    'Close': [105.0] * 252,
    'Volume': [1_000_000] * 252,
})

# Parquet
start = time.time()
df.to_parquet('cache.parquet')
df_pq = pd.read_parquet('cache.parquet')
pq_time = time.time() - start
pq_size = Path('cache.parquet').stat().st_size

# CSV
start = time.time()
df.to_csv('cache.csv', index=True)
df_csv = pd.read_csv('cache.csv', index_col=0)
csv_time = time.time() - start
csv_size = Path('cache.csv').stat().st_size

print(f"Parquet: {pq_time:.4f}s, {pq_size/1024:.1f}KB")
print(f"CSV:     {csv_time:.4f}s, {csv_size/1024:.1f}KB")
# 출력 예상:
# Parquet: 0.0015s, 8.2KB
# CSV:     0.0040s, 23.5KB
```

### 설치 가이드

```bash
# pyarrow 기본 설치 (pyproject.toml에 포함)
uv sync

# 또는 fastparquet 사용 (선택, 다소 느림)
# uv pip install fastparquet
```

