# 커스텀 스킬 (Custom Commands) 가이드

## 개요

커스텀 스킬은 Claude Code에서 `/명령어` 형태로 호출할 수 있는 재사용 가능한 프롬프트.
반복적인 작업 패턴을 표준화하고, 팀 전체가 동일한 워크플로우를 공유할 수 있음.

## 설정 파일 위치

| 위치 | 범위 | git 공유 |
|------|------|---------|
| `~/.claude/commands/명령어.md` | 글로벌 (모든 프로젝트) | 아니오 |
| `.claude/commands/명령어.md` | 프로젝트 | 예 |
| `.claude/skills/스킬명/SKILL.md` | 프로젝트 (새 형식) | 예 |
| `~/.claude/skills/스킬명/SKILL.md` | 글로벌 (새 형식) | 아니오 |

> **두 가지 형식**: `commands/` (단일 .md) vs `skills/` (디렉토리 + SKILL.md + 보조 파일)
> 복잡한 스킬은 `skills/` 형식 권장 — 템플릿, 예시, 스크립트를 함께 묶을 수 있음

## 스킬 파일 구조

### 간단한 형식 (commands/)

```markdown
---
description: 이 스킬이 하는 일 (한 줄 요약)
allowed-tools: Edit, Write, Bash, Glob, Grep, Read
model: sonnet
---

여기에 Claude에게 보내는 프롬프트를 작성.
$ARGUMENTS 변수로 사용자 입력을 받을 수 있음.
```

### 디렉토리 형식 (skills/)

```
.claude/skills/code-reviewer/
├── SKILL.md           # 메인 프롬프트 (필수)
├── template.md        # Claude가 채울 템플릿 (선택)
├── examples/          # 참조 예시 (선택)
│   └── sample.md
└── scripts/           # 보조 스크립트 (선택)
    └── helper.sh
```

## frontmatter 전체 옵션

| 필드 | 설명 | 예시 |
|------|------|------|
| `name` | 스킬 이름 → `/name` 으로 호출 | `"code-reviewer"` |
| `description` | 스킬 설명 (필수, 자동 호출 판단에 사용) | `"PR 코드 리뷰 수행"` |
| `argument-hint` | 인자 힌트 | `"[파일경로]"` |
| `allowed-tools` | 사용 가능한 도구 목록 | `"Edit, Bash, Read"` |
| `model` | 사용할 모델 오버라이드 | `"sonnet"`, `"opus"`, `"haiku"` |
| `effort` | 노력 수준 오버라이드 | `"high"`, `"medium"`, `"low"` |
| `disable-model-invocation` | Claude 자동 호출 차단 (수동 `/명령어` 만) | `true` |
| `user-invocable` | `/` 메뉴에 표시 여부 | `false` (자동 전용) |
| `context` | 실행 컨텍스트 격리 | `"fork"` (서브에이전트에서 실행) |
| `agent` | 서브에이전트 타입 | `"Explore"` |
| `hooks` | 스킬 내 훅 정의 | (아래 예시 참조) |

### 변수 치환

- `$ARGUMENTS` 또는 `$0`, `$1` 등 → 사용자가 전달한 인자
- `${CLAUDE_SESSION_ID}` → 현재 세션 ID
- `${CLAUDE_SKILL_DIR}` → SKILL.md가 위치한 디렉토리
- `` `!command` `` → 명령 실행 결과를 인라인 삽입

## 실용 스킬 예시

### /review — 코드 리뷰

`.claude/commands/review.md`:

```markdown
---
description: 변경된 파일의 코드 리뷰를 수행합니다
allowed-tools: Bash, Read, Grep, Glob
model: sonnet
---

현재 브랜치에서 변경된 파일에 대해 코드 리뷰를 수행해줘.

1. `git diff --name-only HEAD~1` 또는 `git diff --name-only main...HEAD`로 변경 파일 확인
2. 각 파일의 변경 사항을 읽고 아래 기준으로 리뷰:

체크리스트:
- [ ] 보안 취약점 (SQL injection, XSS, 하드코딩된 시크릿)
- [ ] 에러 처리 누락
- [ ] 타입 힌트 일관성
- [ ] 네이밍 규칙 준수
- [ ] 불필요한 코드 (dead code, 미사용 import)
- [ ] 테스트 커버리지

결과를 간결하게 정리해줘. 문제없는 항목은 생략.
$ARGUMENTS
```

### /test-gen — 테스트 자동 생성

`.claude/commands/test-gen.md`:

```markdown
---
description: 지정된 파일의 단위 테스트를 생성합니다
allowed-tools: Read, Write, Glob, Grep
model: sonnet
---

$ARGUMENTS 파일을 읽고 단위 테스트를 생성해줘.

규칙:
1. 테스트 파일 위치: tests/unit/test_{원본파일명}.py
2. pytest 사용
3. AAA 패턴 (Arrange-Act-Assert)
4. 네이밍: test_{함수명}_{조건}_{기대결과}
5. 엣지 케이스 포함 (None, 빈 값, 경계값)
6. 기존 테스트 파일이 있으면 추가, 없으면 새로 생성
```

### /deploy-check — 배포 전 점검

`.claude/commands/deploy-check.md`:

```markdown
---
description: 배포 전 필수 점검 항목을 확인합니다
allowed-tools: Bash, Read, Grep, Glob
model: sonnet
---

배포 전 점검을 수행해줘:

1. **린트**: ruff check 실행 → 에러 0개 확인
2. **타입 체크**: mypy 실행 (설정된 경우)
3. **테스트**: pytest 실행 → 전체 통과 확인
4. **시크릿 검사**: .env, credentials, API 키가 커밋되지 않았는지 확인
5. **미커밋 변경**: git status로 uncommitted 파일 확인
6. **의존성**: requirements.txt 와 실제 import 일치 확인

결과를 체크리스트 형태로 보고해줘.
```

### /explain — 코드 설명

`.claude/commands/explain.md`:

```markdown
---
description: 지정된 코드의 동작을 설명합니다
allowed-tools: Read, Grep, Glob
model: sonnet
---

$ARGUMENTS 를 읽고 다음을 설명해줘:

1. **목적**: 이 코드가 무엇을 하는지 (1-2문장)
2. **핵심 로직**: 주요 흐름을 단계별로
3. **의존성**: 어떤 외부 모듈/함수를 사용하는지
4. **주의점**: 잠재적 이슈나 특이한 패턴

기술 수준에 맞춰 설명 (간결하게).
```

### /migrate — DB 마이그레이션 생성

`.claude/commands/migrate.md`:

```markdown
---
description: DB 마이그레이션 스크립트를 생성합니다
allowed-tools: Read, Write, Bash, Grep
model: sonnet
---

$ARGUMENTS 에 대한 DB 마이그레이션 스크립트를 생성해줘.

1. 현재 모델 파일(models.py)을 읽고 변경사항 파악
2. scripts/ 디렉토리에 마이그레이션 스크립트 생성
3. 파일명: scripts/migrate_{YYYYMMDD}_{설명}.py
4. UP/DOWN 양방향 마이그레이션 포함
5. 데이터 손실 가능성이 있으면 경고
```

## 사용법

```bash
# 인자 없이
/review

# 인자와 함께
/test-gen issuance_be_fastapi/domain/board/crud/session.py
/explain issuance_be_fastapi/auth/security.py:45-80
```

## 팁

- 스킬 프롬프트에 프로젝트별 규칙을 포함하면 일관된 결과
- `allowed-tools`로 스킬 범위를 제한하면 안전성 증가
- `model: haiku`로 간단한 작업은 비용 절감
- `$ARGUMENTS`가 비어있을 때의 기본 동작 정의 권장
