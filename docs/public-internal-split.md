# ThePeach Public And Internal Split

## Why The Split Exists

ThePeach remains a production platform exposed on the public internet for normal user and service traffic. The platform is not being moved into an internal-only network.

What changes is the exposure model:

- public traffic stays on `thepeach.thesysm.com`
- internal operations and high-risk routes move behind `ops.thesysm.com`
- optional dedicated internal auth traffic can use `auth-internal.thesysm.com`

This keeps centralized authentication in `accounts` while reducing the blast radius of administrative and routing-sensitive APIs.

## Public Endpoints

Public endpoints remain on `thepeach.thesysm.com`.

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

These routes remain deterministic and AI-callable.

## Internal Endpoints

Internal endpoints require:

- an internal host
- any configured proxy/access headers

Internal routes:

- `/admin/`
- `/api/v1/auth/internal/`
- `/api/v1/auth/internal/events/summary/`
- `/api/v1/gateway/internal/`
- `/api/v1/gateway/internal/routes/`
- `/api/v1/gateway/internal/resolve/`
- `/api/v1/gateway/tools/applications/`

Legacy aliases:

- `/api/v1/gateway/routes/`
- `/api/v1/gateway/resolve/`

The aliases are still present for migration safety, but they are now guarded as internal-only.

## Access Enforcement

ThePeach enforces internal access in two layers:

1. Nginx host routing
2. Django internal route guards

Django checks:

- request host must match `THEPEACH_INTERNAL_ALLOWED_HOSTS`
- if configured, every header in `THEPEACH_INTERNAL_REQUIRED_HEADERS` must be present

This is intentionally generic so Cloudflare Access headers can be enforced without hardcoding a vendor secret into the codebase.

## Cloudflare Integration Points

Recommended Cloudflare role split:

- public hostname: normal proxied public application
- ops hostname: protected by Cloudflare Access
- tunnel/origin routing: `cloudflared` continues forwarding to local Nginx

Typical headers to validate via `THEPEACH_INTERNAL_REQUIRED_HEADERS`:

- `CF-Access-Authenticated-User-Email`
- `CF-Access-Jwt-Assertion`

The code only checks header presence. If stricter validation is needed later, the internal access utilities in `common/internal_access.py` are the extension point.

## Logging

Internal route grants and denials are written to:

- database-backed `logs_systemlog`
- filesystem-backed `security.log`

Auth and gateway operations continue to write to:

- `auth.log`
- `api.log`
- `application.log`
- `error.log`

## Rollout Guidance

1. Deploy the Django code first.
2. Add the new environment variables.
3. Install the dedicated public and internal Nginx server blocks.
4. Put `ops.thesysm.com` and optional `auth-internal.thesysm.com` behind Cloudflare Access.
5. Validate public and internal smoke tests.
6. Move operators and automation to the internal routes.
7. Remove legacy aliases only after downstream callers are migrated.
