# ThePeach Production Deployment

## Topology

`Client -> Cloudflare -> Nginx -> Gunicorn -> Django`

ThePeach assumes:

- Django is not directly exposed
- Nginx serves static and media files
- Gunicorn serves application traffic
- PostgreSQL is the primary database

## Settings Modules

- Local: `project.settings.local`
- Production: `project.settings.prod`

Runtime rule:

- `manage.py` defaults to `project.settings.local` for developer convenience
- WSGI/ASGI startup does not default to local settings
- production must set `DJANGO_SETTINGS_MODULE=project.settings.prod` explicitly

## Required Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Recommended:

- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_LOG_DIR=/logs/thepeach`
- `DJANGO_SECURE_SSL_REDIRECT=true`

## Proxy / SSL Notes

- `SECURE_PROXY_SSL_HEADER` trusts `X-Forwarded-Proto`
- `USE_X_FORWARDED_HOST` is enabled in production
- secure cookies are enabled in production
- HSTS is enabled in production

## Static and Media

- `STATIC_ROOT=staticfiles/`
- `MEDIA_ROOT=media_files/`
- Nginx should serve both directly

## Logging

Runtime log files are separated into:

- `application.log`
- `error.log`
- `auth.log`
- `api.log`

Production default log directory:

- `/logs/thepeach`

## Migrations and Rollback

Deploy sequence:

1. release code
2. apply migrations
3. reload Gunicorn
4. verify `/api/v1/health/`

Example Gunicorn environment:

- `DJANGO_SETTINGS_MODULE=project.settings.prod`

Rollback:

1. stop rollout
2. restore previous release
3. only reverse migrations if the migration itself is confirmed as the failure source

## Auth Route Note

Canonical auth namespace:

- `/api/v1/auth/`

Legacy `/api/v1/accounts/` auth routing has been removed from the gateway surface.
