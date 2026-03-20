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
- `THEPEACH_PUBLIC_DOMAIN=thepeach.thesysm.com`
- `THEPEACH_OPS_DOMAIN=ops.thesysm.com`
- `THEPEACH_INTERNAL_AUTH_DOMAIN=auth-internal.thesysm.com`
- `THEPEACH_INTERNAL_ALLOWED_HOSTS=ops.thesysm.com,auth-internal.thesysm.com`
- `THEPEACH_INTERNAL_REQUIRED_HEADERS=CF-Access-Authenticated-User-Email`

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
- `security.log`

Production default log directory:

- `/logs/thepeach`

## Migrations and Rollback

Deploy sequence:

1. release code
2. apply migrations
3. restart Gunicorn as `cskang`
4. verify `/api/v1/health/`

Example Gunicorn environment:

- `DJANGO_SETTINGS_MODULE=project.settings.prod`

Rollback:

1. stop rollout
2. restore previous release
3. only reverse migrations if the migration itself is confirmed as the failure source

## Host Deployment Assets

The repository ships host deployment assets in:

- `deploy/production/gunicorn_thepeach.service`
- `deploy/production/gunicorn_thepeach.config.py`
- `deploy/production/nginx_thepeach.conf`
- `deploy/production/nginx_thepeach_public.conf`
- `deploy/production/nginx_thepeach_internal.conf`
- `deploy/production/cloudflared_thepeach_ingress.yml`
- `deploy/production/thepeach.env.example`

Recommended installed locations:

- `~/.config/systemd/user/gunicorn_thepeach.service`
- `/etc/thepeach/thepeach.env`
- `/etc/nginx/sites-available/thepeach`
- `/etc/nginx/sites-enabled/thepeach`

Recommended public hostname:

- `thepeach.thesysm.com`

Recommended internal hostnames:

- `ops.thesysm.com`
- `auth-internal.thesysm.com`

Recommended runtime paths:

- gunicorn bind: `127.0.0.1:8001`
- static root for nginx: `/var/www/thepeach/static`
- media root for nginx: `/var/www/thepeach/media`
- log directory: `/logs/thepeach`

Cloudflare tunnel note:

- because Cloudflare terminates external HTTPS before forwarding to local nginx over HTTP, the ThePeach nginx site must explicitly set `X-Forwarded-Proto https` when proxying to Gunicorn
- otherwise Django production security will redirect to HTTPS repeatedly

Public/internal split note:

- keep public APIs on `thepeach.thesysm.com`
- route admin and internal operations through `ops.thesysm.com`
- optionally separate sensitive auth operations onto `auth-internal.thesysm.com`
- protect internal hostnames with Cloudflare Access and pass the required identity headers through Nginx

Deployment sequence:

1. install Python dependencies from `requirements/prod.txt`
2. copy `deploy/production/thepeach.env.example` to `/etc/thepeach/thepeach.env` and fill real secrets
3. run `python manage.py collectstatic --noinput` with `DJANGO_SETTINGS_MODULE=project.settings.prod`
4. install the user systemd service and nginx files
5. enable lingering once with `sudo loginctl enable-linger cskang`
6. enable or restart Gunicorn with `systemctl --user enable --now gunicorn_thepeach.service`
7. merge the Cloudflare ingress rule so traffic lands on local Nginx
8. validate with `/api/v1/health/`

Automation helpers:

- installer: `deploy/production/install_thepeach.sh`
- validator: `deploy/production/validate_thepeach.sh`
- one-shot manual runner: `deploy/production/run_thepeach_deploy.sh`
- Gunicorn control wrapper: `deploy/production/gunicornctl.sh`

## Route Classification

Public:

- `/api/v1/auth/`
- `/api/v1/auth/signup/`
- `/api/v1/auth/login/`
- `/api/v1/auth/token/refresh/`
- `/api/v1/auth/logout/`
- `/api/v1/auth/me/`
- `/api/v1/services/`
- `/api/v1/gateway/`
- `/api/v1/gateway/integrations/applications/`
- `/api/v1/health/`
- `/api/v1/gateway/health/`

Internal:

- `/admin/`
- `/api/v1/auth/internal/`
- `/api/v1/auth/internal/events/summary/`
- `/api/v1/gateway/internal/`
- `/api/v1/gateway/internal/routes/`
- `/api/v1/gateway/internal/resolve/`
- `/api/v1/gateway/tools/applications/`

Compatibility aliases now treated as internal-only:

- `/api/v1/gateway/routes/`
- `/api/v1/gateway/resolve/`

## Rollout Plan

1. Deploy code with the Django internal route guard enabled.
2. Add the new environment variables and reload Gunicorn.
3. Install the split Nginx templates for public and internal hostnames.
4. Enable Cloudflare Access on `ops.thesysm.com` and optional `auth-internal.thesysm.com`.
5. Move operators and automation from legacy gateway routes to `/api/v1/gateway/internal/...`.
6. Validate that public auth and service APIs remain reachable from `thepeach.thesysm.com`.
7. Remove compatibility aliases only after all callers are migrated.

## Smoke Checklist

- `GET /api/v1/health/` on `thepeach.thesysm.com`
- `POST /api/v1/auth/login/` on `thepeach.thesysm.com`
- `GET /api/v1/services/` with valid auth on `thepeach.thesysm.com`
- `GET /admin/` returns blocked on `thepeach.thesysm.com`
- `GET /api/v1/auth/internal/` succeeds only on an allowed internal host
- `POST /api/v1/gateway/internal/resolve/` succeeds only on an allowed internal host
- `security.log` records both allowed and denied internal route access

## Rollback Notes

- revert Nginx host split first if operators are locked out unexpectedly
- clear `THEPEACH_INTERNAL_REQUIRED_HEADERS` temporarily only if Cloudflare Access header propagation is the failure point
- keep the legacy internal aliases during rollback to avoid breaking existing automation
- revert the Django code change last so public/internal route policies stay aligned with the active proxy configuration

## Auth Route Note

Canonical auth namespace:

- `/api/v1/auth/`

Legacy `/api/v1/accounts/` auth routing has been removed from the gateway surface.
