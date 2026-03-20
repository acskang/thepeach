# Project Structure And Conventions

## Current Repository Shape

The current repository uses root-level Django apps and `project/settings/`.

Core domains:

- `accounts/`
- `common/`
- `gateway/`
- `media/`
- `services/`
- `logs/`

## Supporting Directories

- `templates/` for server-rendered operator UI
- `static/` for platform styles and static assets
- `media_files/` for uploaded shared media
- `docs/` for platform documentation
- `requirements/` for dependency entry points
- `codex-history/` for append-only Codex work history

## Conventions

- APIs live under `/api/v1/`
- templates extend the common base layout
- file uploads are validated server-side
- production runtime must use explicit settings selection
- commit history should stay rollback-friendly
