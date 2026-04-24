# CLAUDE.md

<!--
  이 파일은 Claude Code가 매 턴마다 자동 로드하는 프로젝트 지침서입니다.
  토큰 경제학: ~10k 토큰 이내 권장 (200k 윈도우의 5% 이하)

  작성 원칙:
  1. 코드에서 읽을 수 있는 건 여기 적지 않는다 (DRY)
  2. 구체적 명령 > 일반론 ("좋은 코드를 짜줘" ← 비효과적)
  3. 예제 코드는 최소한으로 — 실제 코드 파일을 참조시키는 게 나음
  4. 자주 변경되는 정보는 memory로 분리
-->

## Commands

```bash
# 개발 서버 실행
{{DEV_SERVER_COMMAND}}

# 테스트 실행
{{TEST_COMMAND}}

# 린트/포맷
{{LINT_COMMAND}}
{{FORMAT_COMMAND}}

# 빌드
{{BUILD_COMMAND}}
```

## Architecture

{{PROJECT_TYPE}} — {{ARCHITECTURE_PATTERN}} 아키텍처

### Tech Stack
- **Runtime**: {{LANGUAGE}} {{VERSION}}
- **Framework**: {{FRAMEWORK}} {{FRAMEWORK_VERSION}}
- **Database**: {{DATABASE}}
- **ORM/Query**: {{ORM}}
- **Auth**: {{AUTH_METHOD}}
- **Package Manager**: {{PACKAGE_MANAGER}}

### Project Structure

<!--
  전체 디렉토리를 나열하지 말 것.
  Claude가 실제로 참조해야 하는 핵심 디렉토리만 기술.
  나머지는 Glob/Grep으로 탐색 가능.
-->

```
{{PROJECT_ROOT}}/
├── {{SOURCE_DIR}}/          # 메인 소스 코드
│   ├── {{ENTRY_POINT}}      # 앱 엔트리포인트
│   ├── {{CONFIG_FILE}}      # 설정 로더
│   ├── {{DB_FILE}}          # DB 연결/세션
│   ├── routers/             # API 라우터 (엔드포인트 정의)
│   └── domain/              # 도메인 로직 (models, schemas, crud)
├── tests/                   # 테스트
├── scripts/                 # 관리 스크립트
└── docs/                    # 문서
```

## Key Patterns

<!--
  프로젝트에서 반복적으로 사용하는 패턴만 기술.
  Claude가 새 코드 작성 시 이 패턴을 따라야 함.
  패턴당 3-5줄 코드 예시면 충분.
-->

### Pattern 1: {{PATTERN_NAME}}
```{{LANG}}
{{PATTERN_EXAMPLE}}
```

### Pattern 2: {{PATTERN_NAME_2}}
```{{LANG}}
{{PATTERN_EXAMPLE_2}}
```

## API Endpoints

<!--
  활성 엔드포인트만 나열. 비활성/미구현은 별도 표시.
  상세 스펙은 docs/ 문서를 참조시킬 것.
-->

| 카테고리 | 엔드포인트 | 설명 |
|---------|-----------|------|
| {{CATEGORY}} | `{{METHOD}} {{PATH}}` | {{DESCRIPTION}} |

## Development Status

<!--
  현재 진행 상태를 한눈에 파악할 수 있게.
  완료/진행중/미완료만 표시.
-->

| 영역 | 상태 | 비고 |
|------|------|------|
| {{AREA}} | {{STATUS}} | {{NOTE}} |

## Configuration

{{CONFIG_DESCRIPTION}}

## Related Docs

<!--
  docs/ 내 문서 링크. Claude가 필요할 때 읽도록.
  모든 문서를 CLAUDE.md에 인라인하지 말 것.
-->

- [{{DOC_NAME}}]({{DOC_PATH}}) — {{DOC_DESCRIPTION}}
