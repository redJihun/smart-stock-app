# [AGENT REVIEW & KNOWLEDGE UPDATE]

## 1. 태스크 맥락 (Context)
- 현재 작업 브랜치/워크트리: {{branch_name}}
- 원래 목표: {{task_description}}
- 변경된 파일 목록: {{changed_files}}

## 2. 코드 품질 검토 (Code Quality Review)
다음 기준에 따라 저지능(Worker) 에이전트가 작성한 코드를 엄격히 검토해줘:
1. **정합성**: `CLAUDE.md`의 아키텍처 가이드라인을 준수했는가?
2. **중복성**: 기존 유틸리티나 함수를 재활용하지 않고 새로 만든 부분은 없는가?
3. **안정성**: 에러 핸들링(Try-Except 등)과 로그 기록이 누락되지 않았는가?
4. **가독성**: 변수명과 함수명이 도메인 지식을 잘 반영하고 있는가?

## 3. 지식 기반 업데이트 (Knowledge/Memory Update)
이번 작업 과정에서 발생한 이슈나 학습한 패턴을 바탕으로 규칙을 개선해줘:
- **실수 방지**: Worker가 반복적으로 실수한 패턴이 있다면 `CLAUDE.md`의 [Rules] 섹션에 추가할 내용을 제안해.
- **새로운 발견**: 이번에 새롭게 도입한 라이브러리 사용법이나 최적화 기법이 있다면 'Best Practices'로 기록해.

## 4. 형상 관리 제안 (Git Management)
- **커밋 메시지**: Conventional Commits 규격(feat, fix, refactor 등)에 맞춰 '의도'가 드러나게 작성해줘.
- **다음 작업**: 현재 상태에서 바로 이어가야 할 잔여 작업(TODO) 목록을 뽑아줘.

---
[지시사항]
- 결과 검토 중 치명적인 결함이 발견되면 승인(Approve)하지 말고 수정 지시 사항을 요약해줘.
- 문제없다면 "LGTM (Looks Good To Me)"과 함께 업데이트할 규칙 내용을 출력해.
