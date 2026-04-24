# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

이 레포는 Claude Code 프로젝트에 복사해서 쓰는 **템플릿 모음**이다. 실행 가능한 코드가 아니라 마크다운 문서와 설정 파일 예시들로 구성되어 있다.

## Architecture

```
claude_code/
├── CLAUDE.template.md       # 프로젝트 CLAUDE.md 작성용 템플릿
├── AUTHORING-GUIDE.md       # CLAUDE.md & rules 효과적 작성법
├── CHEATSHEET.md            # Claude Code 세션 명령어 빠른 참조
├── rules/                   # .claude/rules/에 배포할 규칙 파일 11개
├── memory/                  # 메모리 시스템 템플릿 + 타입별 예시
├── hooks/                   # Hook 설정 가이드 + 예시 스크립트
├── mcp/                     # MCP 서버 연동 가이드
├── skills/                  # 커스텀 스킬 작성 가이드
└── settings/                # settings.json / keybindings.json 예시
```

## Key Concepts

**계층 구조**: CLAUDE.md(항상 로드) → `.claude/rules/*.md`(항상 로드) → memory(선택적 로드)

**토큰 경제학**: CLAUDE.md는 매 턴마다 전체 로드되므로 200줄 이내로 유지한다. 자주 변하는 정보는 memory로, 반복 교정 내용은 rules로 분리한다.

**템플릿 사용법**: `{{placeholder}}` 를 프로젝트에 맞게 교체. CLAUDE.template.md → 프로젝트 루트, rules/*.md → `.claude/rules/`.

## Rules 파일 목적

| 파일 | 용도 |
|------|------|
| `code-quality.md` | 함수 크기, 명명 규칙, early return 등 |
| `git-workflow.md` | 커밋 메시지, 브랜치, PR 컨벤션 |
| `security.md` | OWASP, 시크릿 관리, 입력 검증 |
| `testing.md` | 테스트 작성 규칙, 커버리지 기준 |
| `communication-style.md` | Claude 응답 언어·형식·길이 제어 |
| `scope-constraints.md` | 요청 없는 파일 생성·리팩토링 방지 |
| `error-handling.md` | 에러 처리·복구 패턴 |
| `agent-patterns.md` | 서브에이전트 위임 패턴 |
| `context-management.md` | 컨텍스트 윈도우 최적화 |
| `meta-prompting.md` | 메타 프롬프팅 기법 8가지 |
| `domain-vocabulary.md` | 도메인 용어 정의 템플릿 |

## 새 템플릿 추가 시

- `{{placeholder}}` 형식으로 변수 표시
- 파일 상단에 사용 목적과 배포 경로 주석 포함
- README.md의 구조 섹션에 항목 추가
