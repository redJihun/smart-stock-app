# 서브에이전트 활용 패턴

## 에이전트 선택 기준

| 작업 유형 | 에이전트 | 파라미터 |
|----------|---------|---------|
| 코드 탐색, 파일 찾기 | Explore | `subagent_type="Explore"` |
| 구현 계획 수립 | Plan | `subagent_type="Plan"` |
| 독립적 코드 구현 | general-purpose | `isolation: "worktree"` |
| 빌드/테스트 실행 | general-purpose | 기본 |
| Claude Code 관련 질문 | claude-code-guide | `subagent_type="claude-code-guide"` |

## 병렬 실행 패턴

### 독립 탐색 병렬화 (권장)

```
# 서로 다른 영역을 동시에 탐색
Agent-1: "auth 모듈의 JWT 토큰 검증 로직 분석"
Agent-2: "routers/에서 인증이 적용되지 않은 엔드포인트 목록화"
→ 두 결과를 합쳐서 의사결정
```

### 독립 구현 병렬화 (주의)

```
# 서로 다른 파일을 동시에 수정
Agent-1 (worktree): "tests/unit/test_auth.py 작성"
Agent-2 (worktree): "tests/unit/test_crud.py 작성"
→ 병합 시 충돌 없음을 보장
```

## 프롬프트 작성 원칙

### 좋은 프롬프트

```
"issuance_be_fastapi/routers/auth.py 파일을 읽고,
login 엔드포인트의 JWT 토큰 생성 로직에서
refresh_token 관련 코드가 있는지 확인해줘.
파일을 수정하지 말고 조사만 해줘."
```

### 나쁜 프롬프트

```
"프로젝트를 전체적으로 살펴보고 인증 관련 문제를 찾아줘"
→ 범위가 너무 넓음, 토큰 낭비
```

## 에이전트 제한

- 동시 에이전트 **4-5개 이하** — 그 이상은 컨텍스트 비용 급증
- 각 에이전트에 **단일 책임** 부여
- 에이전트에게 **수정할 파일 목록을 명시**
- worktree 에이전트는 완료 후 자동 정리됨

## 모델 선택

```
Haiku (model: "haiku"):
  - 기존 패턴 따르는 CRUD 생성
  - 반복적 코드, 보일러플레이트
  - 린트/포맷 수정, 문서 갱신

Sonnet (model: "sonnet"):
  - 탐색, 분석, 일반 구현
  - 대부분의 작업에 적합

Opus (model: "opus"):
  - 아키텍처 설계, 보안 코드
  - 복잡한 알고리즘, 디버깅
```
