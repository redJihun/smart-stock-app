# MCP 서버 설정 가이드

## 개요

MCP(Model Context Protocol)는 Claude Code에 외부 도구/데이터 소스를 연결하는 프로토콜.
Claude가 DB 쿼리, API 호출, 파일시스템 접근 등을 직접 수행할 수 있게 해줌.

## 설정 파일 위치

| 파일 | 범위 | 공유 |
|------|------|------|
| `~/.claude/settings.json` → `mcpServers` | 글로벌 (모든 프로젝트) | 개인 |
| `.claude/mcp.json` | 프로젝트 | git으로 팀 공유 가능 |

## .claude/mcp.json 구조

```json
{
  "mcpServers": {
    "서버이름": {
      "command": "실행 명령",
      "args": ["인자1", "인자2"],
      "env": {
        "환경변수": "값"
      }
    }
  }
}
```

## 실용 MCP 서버 예시

### 1. MySQL 데이터베이스

```json
{
  "mcpServers": {
    "mysql": {
      "command": "uvx",
      "args": [
        "mcp-server-mysql",
        "--host", "192.168.20.191",
        "--port", "3307",
        "--user", "root",
        "--password", "your_password",
        "--database", "your_database"
      ]
    }
  }
}
```

사용: `mcp__mysql__mysql_query` 도구로 SQL 실행

### 2. PostgreSQL 데이터베이스

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-postgres",
        "postgresql://user:pass@localhost:5432/dbname"
      ]
    }
  }
}
```

### 3. 파일시스템 (제한된 디렉토리)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-filesystem",
        "/home/user/workspace",
        "/home/user/docs"
      ]
    }
  }
}
```

### 4. GitHub

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

### 5. Slack

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-xxxxxxxxxxxx"
      }
    }
  }
}
```

### 6. 웹 검색 (Brave Search)

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA_xxxxxxxxxxxx"
      }
    }
  }
}
```

## 활성화 설정

`.claude/settings.json` 또는 `.claude/settings.local.json`:

```json
{
  // 모든 MCP 서버 자동 활성화
  "enableAllProjectMcpServers": true,

  // 또는 특정 서버만 선택 활성화
  "enabledMcpjsonServers": ["mysql", "github"]
}
```

## 보안 주의사항

- MCP 서버 설정에 비밀번호/토큰 포함 시 `.claude/mcp.json`을 `.gitignore`에 추가
- 또는 환경 변수로 분리: `"password": "$DB_PASSWORD"` (env 필드 활용)
- `enableAllProjectMcpServers: true`는 신뢰하는 프로젝트에서만 사용
- MCP 서버는 시스템 리소스에 접근할 수 있으므로 신뢰할 수 있는 서버만 사용

## 디버깅

```bash
# MCP 서버 상태 확인
# Claude Code 내에서:
/mcp

# 또는 /context 로 MCP 도구 목록 확인
/context
```
