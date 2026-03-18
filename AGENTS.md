# AGENTS.md

## Project Operating Context

- This repository is the core platform project `ThePeach`.
- Future Codex sessions must read this file before making changes.
- Future Codex sessions must also inspect `codex-history/` before starting substantial work, with priority on the latest monthly history file.

## Codex History Policy

- The project-local Codex history directory is `/home/cskang/ganzskang/ThePeach/codex-history/`.
- History files are append-only cumulative Markdown files.
- Fixed filename rule: one file per month named `YYYY-MM.md`.
- Example: March 2026 history is stored in `codex-history/2026-03.md`.
- New Codex work in the same month must be appended to the existing monthly file, not written to a new ad hoc filename.
- Existing history files must not be deleted, renamed, truncated, rewritten for cleanup, or compacted away.
- Existing history files must not be “cleaned up” for brevity. Corrections should be appended as new entries.
- Each appended history entry should include:
  - date and time
  - user request summary
  - implementation/result summary
  - notable files changed
  - validation status

## Session Start Rule

- At the start of a new Codex session for this repository:
  1. Read `AGENTS.md`.
  2. Read `codex-history/README.md`.
  3. Read the latest relevant monthly file in `codex-history/`.
  4. Continue the append-only history in the current month’s file.

## Repository Safety Rule

- Do not delete or clean up files under `codex-history/` unless the user explicitly overrides this policy.
