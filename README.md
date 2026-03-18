# ThePeach

ThePeach is a production-oriented Django platform for centralized authentication, application governance, reusable media assets, and integration-ready APIs.

## Purpose

ThePeach provides the shared platform layer for:

- centralized JWT-based identity and future SSO expansion
- application and feature registration
- reusable media and brand asset management
- gateway-style API entry and integration surfaces
- operational logging and auditability

Application teams should build business logic on top of ThePeach rather than re-implementing platform concerns.

## Current Repository Structure

This repository currently uses root-level Django apps and `project/settings/`.

```text
ThePeach/
├── accounts/
├── common/
├── gateway/
├── logs/
├── media/
├── services/
├── project/
│   └── settings/
├── templates/
├── static/
├── docs/
├── requirements/
└── codex-history/
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements/local.txt
```

3. Set environment variables as needed. For local development, `manage.py` defaults to `project.settings.local`.
4. Apply migrations:

```bash
python manage.py migrate
```

5. Run the server:

```bash
python manage.py runserver
```

## Production Summary

- Production settings module: `project.settings.prod`
- Deployment path: Cloudflare -> Nginx -> Gunicorn -> Django
- Nginx should serve `/static/` and `/media/` directly
- Gunicorn should run Django with an explicit `DJANGO_SETTINGS_MODULE=project.settings.prod`
- Runtime logs should be written to a filesystem-backed log directory, not committed to Git

## Git / GitHub

- Primary remote target: `git@github.com:acskang/thepeach.git`
- Stable branch: `main`
- Integration branch: `dev`
- Do not commit `.env`, local databases, uploaded media, runtime logs, or local cache artifacts

See [docs/repository-management.md](/home/cskang/ganzskang/ThePeach/docs/repository-management.md) for repository governance details.
