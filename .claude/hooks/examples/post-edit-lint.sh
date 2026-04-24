#!/bin/bash
# Post-Edit Lint Hook
# Automatically runs ruff lint after file edits

# Path of the edited file (passed by Claude Code)
FILE_PATH="${1:-.}"

# Target Python files only
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

# Run from project root
cd "$(git rev-parse --show-toplevel)" 2>/dev/null || exit 0

# Activate environment and run lint (5s timeout)
timeout 5s bash -c "
  source .venv/bin/activate 2>/dev/null || true
  uv run ruff check --select=E,W,F \"$FILE_PATH\" 2>&1 | head -20
" || true

# Proceed with file save even if lint fails (non-blocking)
exit 0
