# Claude Code Hooks 가이드

## 개요

Hooks는 Claude Code의 특정 이벤트 발생 시 자동으로 쉘 명령을 실행하는 시스템.
`.claude/settings.json` 또는 `~/.claude/settings.json` 에 정의.

## 설정 구조

```json
{
  "hooks": {
    "{{EVENT_NAME}}": [
      {
        "matcher": "{{TOOL_NAME_PATTERN}}",
        "command": "{{SHELL_COMMAND}}",
        "timeout": 30000
      }
    ]
  }
}
```

## 사용 가능한 이벤트 (전체)

| 이벤트 | 시점 | 용도 |
|--------|------|------|
| `SessionStart` | 세션 시작 시 | 환경 초기화, 로깅 시작 |
| `InstructionsLoaded` | CLAUDE.md/rules 로드 후 | 설정 검증 |
| `UserPromptSubmit` | 사용자 입력 제출 시 | 입력 전처리, 로깅 |
| `PreToolUse` | 도구 실행 전 | 도구 호출 검증, 차단, 로깅 |
| `PermissionRequest` | 권한 요청 시 | 자동 승인/거부 로직 |
| `PostToolUse` | 도구 실행 후 (성공) | 결과 검증, 후처리 (포맷팅 등) |
| `PostToolUseFailure` | 도구 실행 후 (실패) | 에러 로깅, 복구 |
| `Notification` | 알림 발생 시 | 데스크톱 알림, Slack 통보 |
| `SubagentStart` | 서브에이전트 시작 시 | 서브에이전트 모니터링 |
| `SubagentStop` | 서브에이전트 종료 시 | 서브에이전트 결과 검증 |
| `Stop` | Claude 응답 종료 시 | 최종 검증, 알림 |
| `SessionEnd` | 세션 종료 시 | 정리, 로깅 종료 |

## Hook 타입 (4가지)

| 타입 | 설명 | 용도 |
|------|------|------|
| `command` | 쉘 명령 실행 | 린트, 포맷, 파일 조작 |
| `http` | HTTP POST 전송 | 외부 서비스 알림, 웹훅 |
| `prompt` | LLM에게 검증 요청 | 복잡한 조건 판단 |
| `agent` | 에이전트로 검증 | 테스트 실행 등 복잡한 검증 |

## matcher 패턴

- 특정 도구: `"Edit"`, `"Write"`, `"Bash"`
- 복수 도구: `"Edit|Write"` (파이프로 OR)
- MCP 도구: `"mcp__github__search_repositories"`
- 와일드카드: 생략 또는 빈 문자열 (모든 도구)

## Hook 입출력

- **입력**: stdin으로 JSON 전달 (`session_id`, `cwd`, `tool_name`, `tool_input` 등)
- **출력**: exit code로 제어 — `0` = 허용, `2` = 차단
- **stdout**: Claude에게 피드백으로 전달
- **stderr**: 사용자에게 경고로 표시

## 실용 예제

### 1. 파일 수정 후 자동 린트

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "command": "if echo $CLAUDE_FILE_PATH | grep -q '\\.py$'; then ruff check $CLAUDE_FILE_PATH --fix --quiet 2>/dev/null; fi"
      }
    ]
  }
}
```

### 2. Write 시 백업 생성

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "command": "if [ -f \"$CLAUDE_FILE_PATH\" ]; then cp \"$CLAUDE_FILE_PATH\" \"$CLAUDE_FILE_PATH.bak\"; fi"
      }
    ]
  }
}
```

### 3. 작업 완료 데스크톱 알림

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "command": "notify-send 'Claude Code' \"$CLAUDE_NOTIFICATION\" 2>/dev/null || true"
      }
    ]
  }
}
```

### 4. 위험한 Bash 명령 차단

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "if echo \"$CLAUDE_BASH_COMMAND\" | grep -qE 'rm\\s+-rf|DROP\\s+TABLE|TRUNCATE'; then echo 'BLOCKED: 위험한 명령이 감지되었습니다' >&2; exit 1; fi"
      }
    ]
  }
}
```

## 환경 변수

Hook 스크립트에서 사용 가능한 환경 변수:

| 변수 | 설명 | 이벤트 |
|------|------|--------|
| `CLAUDE_FILE_PATH` | 대상 파일 경로 | Edit, Write, Read |
| `CLAUDE_BASH_COMMAND` | 실행할 Bash 명령 | Bash |
| `CLAUDE_NOTIFICATION` | 알림 메시지 | Notification |
| `CLAUDE_TOOL_NAME` | 실행된 도구 이름 | 모든 이벤트 |

## 주의사항

- Hook이 비정상 종료(exit 1)하면 해당 도구 실행이 차단됨
- timeout 기본값: 30초 — 무한 루프 주의
- Hook에서 stdout 출력은 Claude에게 피드백으로 전달
- stderr 출력은 사용자에게 경고로 표시
- Hook 실패가 워크플로우를 막을 수 있으므로 방어적으로 작성 (`|| true`)
