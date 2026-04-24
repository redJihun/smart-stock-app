---
name: reference_external
description: 외부 시스템 접근 정보 — 이슈 트래커, 모니터링 대시보드 등
type: reference
---

## 이슈 트래커
- Jira 프로젝트: PROJ-XXX (이슈 번호 형식)
- 또는 GitHub Issues 사용

## 모니터링
- Grafana 대시보드: http://monitoring.internal/d/main
- API 레이턴시 알림: Slack #ops-alerts

## DB 접근
- 개발 DB: 192.168.x.x:3306 / dev_db
- 테스트 DB: 192.168.x.x:3307 / test_db
- MCP MySQL: `mcp__mysql__mysql_query` 도구로 접근 가능

## 문서
- API 스펙: docs/api-spec.md
- 배포 가이드: docs/DEPLOY.md
- Confluence: https://wiki.internal/project

## 담당자
- 백엔드: 홍 (Slack: @hong)
- 프론트엔드: 김 (Slack: @kim)
- DevOps: 박 (Slack: @park)
