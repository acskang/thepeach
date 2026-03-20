# AGENTS.md

## Project Operating Context

- This repository is the core platform project `ThePeach`.
- Future Codex sessions must read this file before making changes.
- Future Codex sessions must also inspect `codex-history/` before starting substantial work, with priority on the latest timestamped history file.

## Codex History Policy

- The project-local Codex history directory is `/home/cskang/ganzskang/ThePeach/codex-history/`.
- History files use timestamped Markdown filenames.
- Fixed filename rule: `yymmddhh-no.md`.
- `yymmddhh` means 2-digit year, month, day, and hour.
- `no` means a 2-digit sequence number within the same hour.
- Example: the first history file created during `2026-03-20 10:xx` is `codex-history/26032010-01.md`.
- New Codex work must be written using this filename rule instead of monthly history files.
- Existing history files must not be deleted, renamed, truncated, rewritten for cleanup, or compacted away.
- Existing history files must not be “cleaned up” for brevity. Corrections should be appended as new entries.
- Existing monthly history files remain preserved as legacy records.
- New timestamped history files should include:
  - date and time
  - user request summary
  - implementation/result summary
  - notable files changed
  - validation status

## Session Start Rule

- At the start of a new Codex session for this repository:
  1. Read `AGENTS.md`.
  2. Read `codex-history/README.md`.
  3. Read the latest relevant history file in `codex-history/`, prioritizing the newest `yymmddhh-no.md` file when present.
  4. Continue history using a new `yymmddhh-no.md` file that follows the current timestamp and sequence rule.

## Repository Safety Rule

- Do not delete or clean up files under `codex-history/` unless the user explicitly overrides this policy.
