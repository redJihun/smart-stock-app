# Scope Constraint Rules

## Modification Scope
- Only modify the files that were requested
- When fixing bugs, change the minimum number of files
- Do not modify surrounding code under the pretext of "improvement"

## Prohibited Additions
- Do not create new files without being asked
- Do not add docstrings, comments, or type hints to unchanged code
- Do not design for future requirements (YAGNI)
- Do not create helper functions, utilities, or abstractions for one-off tasks

## Protected Files (do not modify without prior confirmation)
- `config.yml`, `.env`, `.env.*`
- `requirements.txt`
- `docker-compose*.yml`, `Dockerfile*`
- `.claude/settings*.json`, `CLAUDE.md`

## Delete / Move
- Delete files only after user confirmation
- Do not delete code that appears unused without confirmation
