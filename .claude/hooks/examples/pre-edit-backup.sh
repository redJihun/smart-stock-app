#!/bin/bash
# Hook: PreToolUse → Edit
# 파일 수정 전 백업 생성 (.bak)
#
# 설정:
# "PreToolUse": [{ "matcher": "Edit", "command": "bash .claude/hooks/pre-edit-backup.sh" }]

if [ -n "$CLAUDE_FILE_PATH" ] && [ -f "$CLAUDE_FILE_PATH" ]; then
    BACKUP_DIR=".claude/backups"
    mkdir -p "$BACKUP_DIR"

    FILENAME=$(basename "$CLAUDE_FILE_PATH")
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "$CLAUDE_FILE_PATH" "$BACKUP_DIR/${FILENAME}.${TIMESTAMP}.bak"

    # 오래된 백업 정리 (7일 이상)
    find "$BACKUP_DIR" -name "*.bak" -mtime +7 -delete 2>/dev/null
fi
