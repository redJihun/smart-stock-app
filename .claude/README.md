# Claude Code Universal Templates

Claude Code 프로젝트에서 범용적으로 사용할 수 있는 컨텍스트, 룰, 메모리, 설정 템플릿 모음.

## 구조

```
claude_temp/
├── README.md                        # 이 파일
├── AUTHORING-GUIDE.md               # CLAUDE.md & Rules 작성 가이드 (효과적인 작성법)
├── CHEATSHEET.md                    # Claude Code 최적화 치트시트 (빠른 참조)
├── CLAUDE.template.md               # CLAUDE.md 범용 템플릿 (프로젝트 루트용)
├── rules/                           # .claude/rules/ 에 넣을 규칙 파일들 (11개)
│   ├── code-quality.md              # 코드 품질·스타일 규칙
│   ├── git-workflow.md              # Git 커밋·브랜치·PR 규칙
│   ├── security.md                  # 보안 규칙 (OWASP, 시크릿 관리)
│   ├── testing.md                   # 테스트 작성 규칙
│   ├── communication-style.md       # Claude 응답 스타일 제어
│   ├── context-management.md        # 컨텍스트 윈도우 최적화
│   ├── error-handling.md            # 에러 처리·복구 패턴
│   ├── agent-patterns.md            # 서브에이전트 활용 패턴
│   ├── meta-prompting.md            # 메타 프롬프팅 기법 (8가지)
│   ├── scope-constraints.md         # 범위 제약 규칙 (원치 않는 변경 방지)
│   └── domain-vocabulary.md         # 도메인 용어 정의 템플릿
├── memory/                          # 메모리 시스템 템플릿
│   ├── MEMORY.template.md           # 메모리 인덱스 템플릿
│   └── examples/                    # 타입별 메모리 파일 예시 (4개)
│       ├── user_example.md          # user 타입 예시
│       ├── feedback_example.md      # feedback 타입 예시
│       ├── project_example.md       # project 타입 예시
│       └── reference_example.md     # reference 타입 예시
├── settings/                        # 설정 파일 예시 (3개)
│   ├── global-settings.jsonc        # ~/.claude/settings.json 가이드
│   ├── project-settings.jsonc       # .claude/settings.json 가이드
│   └── keybindings.jsonc            # ~/.claude/keybindings.json 가이드
├── hooks/                           # Hook 설정 가이드 + 예시
│   ├── hooks-guide.md               # Hook 시스템 상세 가이드
│   └── examples/                    # 실용 훅 스크립트 (2개)
│       ├── pre-edit-backup.sh       # 파일 수정 전 자동 백업
│       └── post-bash-notify.sh      # 작업 완료 데스크톱 알림
├── mcp/                             # MCP 서버 설정
│   └── mcp-setup-guide.md           # MCP 연동 가이드 (6개 서버 예시)
└── skills/                          # 커스텀 스킬
    └── custom-skill-guide.md        # 커스텀 스킬 작성법 (5개 예시)
```

## 사용법

1. 필요한 파일을 자기 프로젝트에 복사
2. `{{placeholder}}` 부분을 프로젝트에 맞게 수정
3. CLAUDE.md → 프로젝트 루트, rules → `.claude/rules/`, settings → `.claude/`

## 핵심 원칙

- **토큰 경제학**: 매 턴마다 모든 컨텍스트가 로드되므로 간결하게 유지
- **구체성 > 일반론**: "코드를 잘 작성해줘"보다 "함수 500줄 이내, early return 사용" 이 효과적
- **반복 교정 방지**: 한 번 교정한 내용은 rules/feedback 메모리로 영구화
- **계층 활용**: CLAUDE.md(항상 로드) → rules(조건부) → memory(선택적)
