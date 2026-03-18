# 문서 관리

## 디렉토리 구조

```
docs/
  README.md                              # 전체 문서 인덱스 (필수)
  work-logs/                             # 주차별 업무일지 + 장기 관리 문서
    README.md
    BACKLOG.md                           # 장기 예정 업무, 기술부채
    NOTES.md                             # 아이디어, 메모, 참고 링크
    {YYMMDD시작}-{YYMMDD종료}-W{주차}.md  # 주차별 업무일지
  architecture-decision-records/         # ADR
    README.md                            # ADR 인덱스 + 상태 목록
    template.md
    {NNNN}-{주제-kebab-case}.md          # 개별 ADR
```

## 문서 추가 시 갱신 대상

| 추가한 문서 | 함께 갱신할 인덱스 |
|---|---|
| ADR (`architecture-decision-records/*.md`) | `architecture-decision-records/README.md` + `docs/README.md` |
| 주차 업무일지 (`work-logs/*.md`) | `work-logs/README.md` |
| 일반 개발 문서 (`docs/*.md`) | `docs/README.md` |

## ADR 작성 기준

다음 조건 중 하나 이상 해당하면 ADR 작성을 제안한다:

- 되돌리기 어려운 기술 결정 (라이브러리 선택, 아키텍처 패턴 등)
- 여러 선택지를 비교해 채택한 결정
- 나중에 맥락 없이 보면 이상하게 보일 수 있는 결정

ADR 추가 후 두 인덱스(`architecture-decision-records/README.md`, `docs/README.md`)를 반드시 갱신한다.
