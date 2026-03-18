# Repository Management

## Purpose

This repository is the long-term source of truth for ThePeach platform code. Git history is part of platform operations and must support rollback, review, and safe deployment.

## Branch Strategy

- `main`: stable and deployable baseline
- `dev`: ongoing integration branch

Keep the model simple. Avoid complex GitFlow branches unless a real delivery need appears.

## Commit Conventions

Use small, explicit commits with stable prefixes such as:

- `feat:`
- `fix:`
- `refactor:`
- `docs:`
- `test:`
- `chore:`

Examples:

- `chore: prepare ThePeach repository governance`
- `docs: add repository management guide`

## What Must Never Be Committed

Do not commit:

- `.env` or `.env.*`
- secret values or credential files
- local SQLite databases
- uploaded media under `media_files/`
- runtime logs
- local virtual environments
- editor caches and OS junk

## Local vs Production Configuration

- Local CLI usage can rely on `project.settings.local` through `manage.py`
- WSGI and ASGI runtime must use an explicit `DJANGO_SETTINGS_MODULE`
- Production must use `project.settings.prod`
- Do not rely on local defaults in production

## Rollback Mindset

- Keep commits focused and reviewable
- Prefer additive changes over destructive rewrites
- Do not force-push shared branches unless explicitly coordinated
- Ensure migration and deployment changes are traceable in commit history

## GitHub Usage

- Preferred remote: `git@github.com:acskang/thepeach.git`
- Alternate remote: `https://github.com/acskang/thepeach.git`
- Use GitHub for backup, code review, issue tracking, and future CI/CD expansion
- Never store GitHub tokens or SSH private keys in the repository

## Codex History

If Codex is used for implementation work, append repository changes to the current monthly file under `codex-history/` according to the append-only history policy.
