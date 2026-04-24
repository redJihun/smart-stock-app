# Claude Code 최적화 치트시트

## 세션 명령어

| 명령 | 용도 | 타이밍 |
|------|------|--------|
| `/compact` | 이전 대화 압축 | 긴 작업 중간, 컨텍스트 60%+ |
| `/clear` | 전체 초기화 | 작업 전환 시 |
| `/context` | 컨텍스트 사용량 확인 | 수시 |
| `/cost` | 토큰/비용 확인 | 세션 종료 전 |
| `/model` | 모델 변경 | 작업 성격 변경 시 |
| `/memory` | 메모리 확인 | 세션 시작 시 |
| `/mcp` | MCP 서버 상태 | 도구 문제 시 |
| `/fast` | 빠른 응답 모드 토글 | 단순 작업 시 |

## 모델 선택 가이드

| 상황 | 모델 | 이유 |
|------|------|------|
| 일상 코딩, 버그 수정 | Sonnet | 균형 (비용/성능) |
| 아키텍처 설계, 보안 | Opus | 깊은 분석 필요 |
| 보일러플레이트, 문서 | Haiku | 빠르고 경제적 |
| 서브에이전트 구현 | Haiku | 패턴 따라하기 |
| 서브에이전트 탐색 | Sonnet | 판단력 필요 |

## 권한 설정 패턴

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(uv run ruff:*)",
      "Bash(uv run pytest:*)"
    ],
    "deny": [
      "Bash(git push --force:*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

**원칙**: 안전한 읽기 명령 + 빌드/테스트 = allow, 파괴적 명령 = deny

## 파일 체계

```
프로젝트/
├── CLAUDE.md                    # 항상 로드 (150줄 이내!)
├── .claude/
│   ├── settings.json            # 프로젝트 설정 (git 커밋)
│   ├── settings.local.json      # 로컬 오버라이드 (gitignore)
│   ├── mcp.json                 # MCP 서버 정의
│   ├── commands/                # 커스텀 스킬 (/명령어)
│   │   └── review.md
│   └── rules/                   # 모듈별 규칙 (항상 로드)
│       ├── code-quality.md
│       └── security.md
└── docs/                        # 필요 시 참조 (항상 로드 X)
```

## 성능 최적화 Top 5

1. **CLAUDE.md 200줄 이내** — 매 턴 토큰 절약
2. **예시 기반 패턴** — "X.py 따를 것" > 장황한 설명
3. **금지 규칙 명시** — 가장 강력한 행동 제어
4. **서브에이전트 위임** — 탐색은 Explore, 구현은 worktree
5. **/compact 적극 사용** — 60% 넘으면 바로 실행

## 흔한 실수 Top 5

1. CLAUDE.md에 전체 디렉토리 트리 나열 → **Glob으로 대체**
2. CLAUDE.md에 API 스펙 전체 인라인 → **docs/ 링크로 대체**
3. "좋은 코드를 짜줘" 같은 모호한 지시 → **구체적 규칙으로 대체**
4. 모든 에이전트에 같은 컨텍스트 전달 → **최소 필요 정보만**
5. 완료된 작업/outdated 규칙 방치 → **월 1회 정리**

## 빠른 시작 (새 프로젝트)

```bash
# 1. 기본 구조 생성
mkdir -p .claude/{rules,commands}

# 2. CLAUDE.md 작성 (핵심만)
cat > CLAUDE.md << 'EOF'
# CLAUDE.md
## Commands
- Dev: `{{command}}`
- Test: `{{command}}`
- Lint: `{{command}}`

## Architecture
{{한 줄 설명}}

## Key Patterns
- 새 기능: `{{참조파일}}` 패턴 따를 것

## 절대 하지 말 것
- 요청 없이 새 파일 생성 금지
- 주변 코드 리팩토링 금지
- 설정 파일 무단 수정 금지
EOF

# 3. 설정
cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": ["Bash(git log:*)", "Bash(git status:*)"]
  }
}
EOF
```
