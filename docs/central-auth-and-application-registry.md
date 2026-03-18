# ThePeach Central Auth And Application Registry

## Centralized Authentication Concept

ThePeach owns the shared user identity.

- signup creates a centralized platform user in `accounts`
- login issues JWT credentials from `accounts`
- logout applies centralized refresh-token revocation
- `/api/v1/auth/me/` is the stable identity introspection endpoint for current phase integrations

Connected applications should treat ThePeach as the identity source of truth.

## Registered Applications Relationship

ThePeach also owns the registry of connected applications, screens, and features.

- `RegisteredApplication` is the platform record for an application service
- `RegisteredScreen` maps the screens or routed surfaces exposed by that application
- `RegisteredFeature` maps the functional capabilities under the application or screen

This metadata is governance data, not presentation-only data.

It supports:

- future gateway policy and routing
- future admin/operator tooling
- future audit and access review
- future SSO and trusted-app integration
- future AI/MCP-facing capability discovery

## Current JWT-Based SSO Direction

Current phase:

- JWT is the active platform auth mechanism
- applications can trust ThePeach-issued access tokens
- refresh-token logout is centralized in ThePeach
- gateway can expose registered application metadata for controlled integrations

Not yet implemented in this phase:

- full OAuth2 authorization server
- OpenID Connect provider endpoints
- downstream logout propagation to external apps
- service-to-service trust exchange

## Future OAuth2 / OIDC Expansion Path

The current structure keeps expansion possible by:

- keeping auth ownership inside `accounts`
- keeping gateway as an integration boundary instead of an auth engine
- keeping application registration under `services` as platform governance metadata
- separating JWT issuance logic from gateway and service business logic

## API Endpoint Summary

Auth:

- `POST /api/v1/auth/signup/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/token/refresh/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`

Services:

- `GET /api/v1/services/`
- `GET, POST /api/v1/services/applications/`
- `GET, PUT, PATCH /api/v1/services/applications/<id>/`
- `POST /api/v1/services/applications/<id>/deactivate/`
- `GET, POST /api/v1/services/screens/`
- `GET, PUT, PATCH /api/v1/services/screens/<id>/`
- `POST /api/v1/services/screens/<id>/deactivate/`
- `GET, POST /api/v1/services/features/`
- `GET, PUT, PATCH /api/v1/services/features/<id>/`
- `POST /api/v1/services/features/<id>/deactivate/`

Gateway:

- `GET /api/v1/gateway/`
- `GET /api/v1/gateway/health/`
- `GET /api/v1/gateway/integrations/applications/`
- `GET /api/v1/gateway/routes/`
- `POST /api/v1/gateway/resolve/`

## Example Payloads

Signup request:

```json
{
  "email": "user@example.com",
  "full_name": "Platform User",
  "smartphone_number": "+821012345678",
  "password": "StrongPass123"
}
```

Application registration request:

```json
{
  "company_id": "company-uuid",
  "app_code": "ops-console",
  "app_name": "Ops Console",
  "app_description": "Operator portal",
  "app_domain": "ops.example.com",
  "app_base_url": "https://ops.example.com",
  "requires_sso": true
}
```

Standard success envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Standard error envelope:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "error_code",
    "message": "Human-readable message"
  }
}
```
