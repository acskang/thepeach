# ThePeach Architecture Principles

## API First

Every major capability should be reachable through versioned APIs under `/api/v1/`.

## SSO First

Authentication belongs to `accounts`. Other domains must not create their own login silos.

## Reusability First

Shared primitives belong in `common` or a clearly reusable platform domain, not duplicated in feature code.

## Loose Coupling

Apps should communicate through stable contracts, models, serializers, services, and response formats rather than deep implementation leakage.

## AI Ready

ThePeach APIs should remain deterministic, machine-consumable, and suitable for agent or MCP-style usage.

## Production Ready

Platform code must assume real deployment behind Cloudflare, Nginx, Gunicorn, and PostgreSQL. Local development shortcuts must not leak into production runtime behavior.

## Public And Internal Separation

Public APIs must stay reachable for normal user and service traffic. High-risk administrative and operational routes must be isolated explicitly through internal hostnames, proxy policy, and auditable access control rather than by collapsing the whole platform into a private-only deployment.
