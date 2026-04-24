# work-logs

주차별 업무일지 및 장기 관리 문서를 함께 보관합니다.

---

## 장기 관리 문서

| 파일 | 설명 |
|------|------|
| [BACKLOG.md](./BACKLOG.md) | 장기 예정 업무, 기술부채 목록 |
| [NOTES.md](./NOTES.md) | 이해관계자 연락처, 회의 메모, 브리핑 내용 |
| [TASK-TEMPLATE.md](./TASK-TEMPLATE.md) | TASK.md 작성용 템플릿 (Claude Code CLI → Cursor 작업 지시) |
| [RESULT-TEMPLATE.md](./RESULT-TEMPLATE.md) | RESULT.md 작성용 템플릿 (Cursor → Claude Code CLI 결과 보고) |

## 주차별 업무일지

네이밍 컨벤션: `{YYMMDD시작}-{YYMMDD종료}-W{주차번호}.md`

기본 템플릿: [`template.md`](./template.md)

각 파일 포함 내용: 이번 주 처리할 업무 / 병목 요인(Blocker) / 완료된 업무

| 파일 | 기간 |
|------|------|
| ex. [260323-260327-W13.md](./260323-260327-W13.md) | 2026년 3월 23일 ~ 3월 27일 |

## gitignore 처리된 파일 (로컬 전용)

아래 파일은 `.gitignore`에 포함되어 git에 추적되지 않는다.

| 파일 패턴 | 설명 |
|---------|------|
| `[0-9]*.md` | 주차별 업무일지 (개인 업무 추적) |
| `NOTES.md` | 이해관계자 연락처·메모 (민감 정보) |
| `TASK.md` | 현재 진행 중인 작업 지시서 (세션 임시 파일) |
| `RESULT.md` | 현재 진행 중인 결과 보고서 (세션 임시 파일) |
