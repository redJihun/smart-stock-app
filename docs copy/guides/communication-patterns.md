# Communication Patterns & Examples

이 문서는 communication-guide.md의 상세 예제와 패턴을 담습니다. 특정 업무 스타일 참고용입니다.

---

## Effective Communication with Claude

### 1. Be Specific and Detailed

원하는 결과를 명확히 정의하세요.

**나쁜 예:**
```
"프리젠테이션을 만들어 줄 수 있을까?"
```

**좋은 예:**
```
"분기별 판매 회의용 10장 프리젠테이션이 필요합니다.
- Q2 판매 실적
- 상품별 매출 순위
- Q3 목표

각 슬라이드별 핵심 포인트를 포함한 아웃라인을 제공해 주세요."
```

**핵심:**
- 대상 청중과 목적 명시
- 필요한 섹션/요소 나열
- 예상 길이 또는 형식 지정

---

### 2. Use Examples

원하는 형식이나 스타일이 있다면 예제를 제시하세요.

**좋은 예:**
```
"이전에 보낸 이메일과 유사한 톤과 구조로 작성해 주세요:
[예제 이메일]
현재 상황은 [구체적 설명]이므로, 이를 반영한 이메일을 작성해 주세요."
```

**핵심:**
- 기존 산출물을 템플릿으로 제시
- "유사하게 but for [새로운 컨텍스트]" 패턴 활용
- 톤, 구조, 길이 일치성 높음

---

### 3. Break Complex Tasks into Steps

큰 작업은 작은 단계로 분해하세요. Claude와 여러 턴에 걸쳐 작업하면 정확도가 높아집니다.

**예시:**
- Step 1: 기본 구조 설계
- Step 2: 각 섹션 작성
- Step 3: 리뷰 및 수정

---

### 4. Encourage Step-by-Step Thinking

복잡한 분석이 필요할 때는 단계별 사고를 유도하세요.

**예:**
```
"다음을 단계별로 분석해 주세요:
1. 현재 문제점
2. 해결 방안
3. 구현 도전 과제
4. 개선 측정 방법

각 단계마다 이유를 설명해 주세요."
```

**핵심:**
- 명시적 단계 나열 (1. 2. 3. ...)
- 각 단계별 설명 요구
- "왜(Why)"를 명확히 포함

---

### 5. Iterative Refinement

첫 응답이 완벽하지 않으면 피드백을 주세요.

```
"좋은 시작이지만, 다음을 수정해 주세요:
1. 톤을 좀 더 친근하게
2. 고객 사례 추가
3. 두 번째 문단 단축"
```

**핵심:**
- 긍정적 피드백 먼저 ("좋은 시작이지만...")
- 구체적 개선 사항 나열
- 우선순위 명시 (선택적)

---

### 6. Provide Full Context

새 요청마다 필요한 모든 맥락을 포함하세요. Claude는 이전 대화를 기억하지 않습니다.

**전달해야 할 맥락:**
- 업무 목적 (What & Why)
- 제약 조건 (길이, 형식, 대상)
- 참고 자료 (기존 문서, 예제)
- 의존성 (다른 업무와의 연계)

---

## Response Structure Examples

### 1. Action Result (1-2 sentences)

작업 완료 내용을 간결하게 표현하세요.

**좋은 예:**
```
2개의 CRUD API를 추가했습니다.
```

**나쁜 예:**
```
CRUD API (Create, Read, Update, Delete의 약자)를 구현했습니다.
```

**비교:**
- ✓ 좋은 예: 무엇(2개의 API) + 동작(추가) → 3초 이해
- ✗ 나쁜 예: 용어 설명 포함 → 불필요한 길이

---

### 2. Summary Format

필요시 다음 정보를 포함하세요:
- 수정된 파일 목록 (변경사항 명확화)
- 테스트 결과 (검증 증거)
- 문제 발생 시: 원인 + 해결책 (투명성)

**예시:**
```
### Summary
- Modified: domain/alerts/crud.py, routers/dashboard.py
- Test: ✓ All 12 tests pass
- Issue: Handler timeout on slow networks
  → Solution: Added 10s timeout with exponential backoff
```

---

### 3. Next Steps (optional)

사용자 의사결정이 필요할 때만 제시하세요.

**좋은 예:**
```
### Next Steps (choose one)
- Option A: Optimize DB query (fast, requires schema change)
- Option B: Add caching layer (slower deploy, zero schema impact)
Recommended: Option A (3ms vs 50ms latency)
```

---

## Error Reporting Format

### Step 1: Error Encountered
```
[Error 404] Handler not found in database
File: domain/board/crud/handler.py:45
```

### Step 2: Cause Analysis
```
→ query().filter(Handler.id == handler_id).first() returns None
→ Handler ID does not exist in DB or condition error
```

### Step 3: Solution
```
1. 예외 처리 추가
2. 테스트 데이터 확인
```

**핵심:**
- 에러 코드 + 메시지 명시
- Root cause를 화살표(→)로 추적
- 검증 가능한 해결책 제시

---

## Task-Specific Guidance

### Content Creation

**핵심:** 대상 청중, 톤, 구조를 명시하세요.

```
"블로그 포스트: 소규모 사업주 대상 사이버보안 기초
- 기술 용어 최소화
- 실행 가능한 조언
- 친근하고 간결한 톤

1,000자 분량, 상위 5가지 보안 관행을 다루세요."
```

**체크리스트:**
- [ ] 대상 청중 명시 (소규모 사업주)
- [ ] 톤 명시 (친근, 간결)
- [ ] 예상 길이 (1,000자)
- [ ] 주요 내용 (상위 5가지 항목)

---

### Document Summary & Q&A

**핵심:** 구체적인 포커스, 명확한 질문, 인용 요청

```
"[문서 이름]을 읽고:
1. AI 트렌드에 초점한 2문단 요약
2. 상위 3가지 AI 비즈니스 활용 사례
3. 각 답변마다 문서 출처 명시"
```

**체크리스트:**
- [ ] 포커스 영역 명시 (AI 트렌드)
- [ ] 답변 형식 (2문단, 3가지)
- [ ] 인용/출처 요청 (추적성)

---

### Data Analysis

**핵심:** 원하는 형식과 메트릭을 명시하세요.

```
"데이터 분석 결과:
1. 요약 (2-3문장)
2. 핵심 지표 (분기별 매출, 상위 상품 등)
3. 3가지 트렌드 + 데이터 기반 권장사항
4. 시각화 제안"
```

**체크리스트:**
- [ ] 결과 형식 명시 (요약 + 지표 + 트렌드 + 시각화)
- [ ] 메트릭 범위 (분기별, 상위 N개 등)
- [ ] 인사이트 요구 (트렌드 + 권장사항)

---

### Brainstorming

**핵심:** 구체적인 매개변수(수, 유형, 분류)를 제시하세요.

```
"원격팀(20명) 팀빌딩 아이디어:
1. 10가지 협업 활동 제안
2. 각 활동이 팀워크를 어떻게 향상시키는지 설명
3. 저예산/프리미엄 옵션 각 1개"
```

**체크리스트:**
- [ ] 수량 명시 (10가지, 1개)
- [ ] 분류 명시 (저예산/프리미엄)
- [ ] 설명 깊이 (각 활동마다 설명)

---

## Troubleshooting Strategies

### Minimize Hallucinations & Maximize Quality

#### 1. 불확실성 인정 유도
- "모르면 '모르겠습니다'라고 말씀해 주세요"
- 예시: "만약 정확하지 않으면 알려 주세요"

#### 2. 복잡한 작업은 세분화
- 한 턴에 한 단계씩 진행
- 각 단계의 결과를 확인한 후 다음 진행

#### 3. 모든 맥락 포함
- 새 요청마다 필요한 모든 정보 제공
- 문서, 코드 스니펫, 이전 결과 포함

**예시 시나리오:**

❌ **약한 요청:**
```
"성능을 개선해 주세요"
```

✅ **강한 요청:**
```
"GET /handler 엔드포인트 성능을 개선해 주세요.
- 현재: 500ms (100 handler 데이터)
- 목표: 100ms 이하
- 제약: 데이터 형식 변경 불가 (프론트엔드 의존성)

관련 코드:
[파일 경로 + 코드 스니펫]"
```
