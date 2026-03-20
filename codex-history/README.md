# Codex History

This directory stores project-local Codex working history for `ThePeach`.

## File Naming Rule

- History is stored in timestamped Markdown files.
- Fixed filename rule: `yymmddhh-no.md`
- `yymmddhh` is the 2-digit year, month, day, and hour.
- `no` is the 2-digit sequence number for that hour.
- Example: `26032010-01.md`

## Append-Only Rule

- Do not delete existing history files.
- Do not rename existing history files.
- Do not truncate, rewrite, or compact existing history files for cleanup.
- Add corrections or clarifications only as new appended entries.
- Existing monthly files such as `2026-03.md` remain as legacy preserved history and must not be removed.

## Entry Format

Each new history file should include:

- timestamp
- user request summary
- result summary
- notable files changed
- verification status

## Session Reference Rule

Future Codex sessions should read:

1. `/home/cskang/ganzskang/ThePeach/AGENTS.md`
2. the latest relevant file in `/home/cskang/ganzskang/ThePeach/codex-history/`, prioritizing the newest `yymmddhh-no.md` file when present
