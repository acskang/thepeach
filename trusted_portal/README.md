# Trusted Portal

`trusted_portal/` is a separate Django project that consumes ThePeach's existing auth API instead of creating its own user database or login flows.

## Why This Shape

- It matches the repository's Django conventions: a project package with `settings/base.py` and `settings/local.py`.
- It keeps authentication reusable and explicit:
  - `core.auth.client.ThePeachAuthClient` calls ThePeach `/api/v1/auth/me/`
  - `core.auth.authentication.ThePeachRemoteAuthentication` protects DRF endpoints
  - `core.auth.middleware.ThePeachRemoteUserMiddleware` hydrates `request.user` for plain Django views
- It does not create signup, login, password reset, or local user persistence.

## Auth Flow

1. A caller obtains an access token from ThePeach itself.
2. The caller sends `Authorization: Bearer <token>` to this service, or an upstream stores the token in the configured session key.
3. This service calls `GET {THEPEACH_BASE_URL}/api/v1/auth/me/`.
4. If ThePeach returns a valid user payload, the service normalizes it into a request-local `ThePeachRemoteUser`.
5. Authorization decisions use that normalized request context only for the current request.

Default upstream base URL is `https://thepeach.thesysm.com`.
`THEPEACH_FALLBACK_BASE_URLS` is only for optional local development overrides.

## Example Endpoints

- `GET /`
  - Plain Django view.
  - Demonstrates middleware-populated `request.user`.
- `GET /auth/login/`
  - Browser login screen.
  - Submits credentials to ThePeach `/api/v1/auth/login/` through the reusable upstream client.
- `GET /api/v1/example/auth-status/`
  - DRF endpoint protected by `ThePeachRemoteAuthentication`.
  - Returns the normalized authenticated user context.

## Environment

Copy values from `.env.example` or export them directly:

- `TRUSTED_PORTAL_SECRET_KEY`
- `TRUSTED_PORTAL_DEBUG`
- `TRUSTED_PORTAL_ALLOWED_HOSTS`
- `TRUSTED_PORTAL_TIME_ZONE`
- `THEPEACH_BASE_URL`
- `THEPEACH_AUTH_ME_PATH`
- `THEPEACH_AUTH_TIMEOUT_SECONDS`
- `THEPEACH_SESSION_TOKEN_KEY`
- `THEPEACH_FORWARD_HEADERS`
- `TRUSTED_PORTAL_LOG_DIR`
- `TRUSTED_PORTAL_LOG_LEVEL`

## Run

From `/home/cskang/ganzskang/ThePeach/trusted_portal`:

```bash
pip install -r ../requirements/local.txt
python manage.py migrate
python manage.py runserver 8001
```

## Verification

With a ThePeach-issued token:

```bash
curl -H "Authorization: Bearer <access-token>" http://localhost:8001/api/v1/example/auth-status/
```

If ThePeach is unavailable, this service returns `503` instead of silently authenticating locally.

Login relay debug logs are written to `.runtime/logs/auth-debug.log` by default.
