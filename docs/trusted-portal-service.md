# Trusted Portal Service

This document describes the connected Django service located at `/home/cskang/ganzskang/ThePeach/trusted_portal`.

## Authentication Design

The service intentionally does not use Django's built-in auth system as an independent identity store.

- No local signup endpoint
- No local login endpoint
- No local password management
- No custom user model
- No local user synchronization table

Instead, it trusts ThePeach's existing auth API:

- default upstream base URL: `https://thepeach.thesysm.com`
- source of truth endpoint: `GET /api/v1/auth/me/`
- transport: bearer access token or a token previously placed into the configured session key
- normalized request object: `core.auth.models.ThePeachRemoteUser`

## Why DRF Authentication Class Was Chosen

The main protected example surface is an API endpoint, and the repository already centers API-first Django/DRF conventions.

`ThePeachRemoteAuthentication` was chosen because it:

- maps directly onto DRF permission handling
- keeps remote-auth failures explicit at the API boundary
- avoids pretending that a local Django `User` row exists
- remains reusable for additional API views in this service

Middleware is still included so plain Django views can read the same remote auth context without inventing a second auth path.

## Failure Handling

- missing token: request remains anonymous and protected views fail with 403
- ThePeach `401` or `403`: request is rejected as unauthenticated
- ThePeach timeout: `503 thepeach_auth_unavailable`
- ThePeach `5xx`: `503 thepeach_auth_unavailable`
- unexpected payload shape: `502 thepeach_auth_contract_error`

## Files

- `trusted_portal/config/settings/base.py`
- `trusted_portal/core/auth/client.py`
- `trusted_portal/core/auth/authentication.py`
- `trusted_portal/core/auth/middleware.py`
- `trusted_portal/core/auth/models.py`
- `trusted_portal/core/auth/permissions.py`
- `trusted_portal/core/views.py`
- `trusted_portal/core/tests.py`
