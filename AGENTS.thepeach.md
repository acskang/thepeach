# AGENTS.thepeach.md

## 1. Project Definition

ThePeach is a reusable Django-based core platform for the AI era.

Its role is to provide:

- centralized authentication and identity
- shared platform primitives
- gateway-style integration entry points
- media and asset management
- durable logging and operational visibility
- business service hosting structure
- AI/MCP-ready APIs

Application teams should implement business logic on top of the platform instead of rebuilding architecture concerns per service.

## 2. Source Of Truth Concept

ThePeach is knowledge-driven.

Source of truth order:

1. running repository state
2. migrations and database schema
3. documented platform rules in `AGENTS.md` and this file
4. cumulative repository history in `codex-history/`

When code and documentation diverge, resolve the divergence explicitly. Do not silently assume old documentation is correct.

## 3. Codex History Rules

This file must stay compatible with the existing `AGENTS.md` policy.

- `AGENTS.md` remains the repository-wide canonical agent policy file.
- `codex-history/` must be preserved.
- History files are append-only cumulative Markdown files.
- Fixed history filename rule: `YYYY-MM.md`
- For the same month, append to the existing monthly file.
- Do not delete, rename, truncate, compact, or clean up old history files.
- Add corrections as new appended entries.
- New Codex sessions should read:
  1. `AGENTS.md`
  2. `AGENTS.thepeach.md`
  3. `codex-history/README.md`
  4. the latest relevant monthly history file

## 4. Current Project Structure

Current repository structure is root-level app based.

```text
ThePeach/
├── accounts/
├── common/
├── gateway/
├── logs/
├── media/
├── services/
├── codex-history/
├── project/
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       └── prod.py
├── AGENTS.md
├── AGENTS.thepeach.md
└── manage.py
```

## 5. Structure Rules

- Django apps must remain at the repository root.
- Allowed root-level platform apps are:
  - `accounts/`
  - `common/`
  - `gateway/`
  - `logs/`
  - `media/`
  - `services/`
- Do not introduce an `apps/` directory in the current structure.
- Do not rename `project/` to `config/`.
- Settings must continue to live under `project/settings/`.

## 6. Core App Definitions

### `accounts`

Authentication and organization core.

Responsibilities:

- custom user model
- JWT authentication
- SSO-ready identity extension points
- company and department structures
- user-to-company memberships
- user-to-department memberships
- identity-related profile data

### `common`

Shared platform core.

Responsibilities:

- abstract base models
- shared API response helpers
- exception normalization
- pagination standards
- cross-cutting tenancy helpers
- request middleware and shared utilities

### `gateway`

EAI and unified platform entry core.

Responsibilities:

- versioned API entry point
- platform discovery surface
- routing boundary for platform modules
- future proxying, policy enforcement, and integration orchestration

### `media`

Centralized asset registry.

Responsibilities:

- image assets
- reusable logos
- video and embed metadata
- company-scoped asset ownership

### `logs`

Operational visibility and audit core.

Responsibilities:

- API request logs
- authentication event logs
- system logs
- persistent observability data

### `services`

Business service container and discovery layer.

Responsibilities:

- service registry
- company-owned business service metadata
- future modular service boundaries

## 7. Architecture Principles

### API First

- Platform capabilities must be accessible through versioned REST APIs.
- Internal code structure should support API exposure without duplicate logic.

### SSO First

- Authentication authority belongs to `accounts`.
- Other apps must not implement separate auth silos.

### Reusability First

- Shared logic belongs in `common` or a clearly reusable domain module.
- Do not duplicate tenancy, auth, response, or audit patterns across apps.

### Loose Coupling

- Apps should depend on stable contracts, not deep internal details of sibling apps.
- Cross-app coupling should flow through models, serializers, services, permissions, and shared helpers with clear boundaries.

### AI-Ready

- APIs must be predictable, machine-consumable, and JSON-based.
- Platform metadata should remain understandable by AI agents and MCP clients.

## 8. Authentication Rules

- `accounts` is the only authentication authority.
- JWT is the current authentication mechanism.
- SSO, OAuth2, and OpenID Connect extensions must layer into `accounts`, not parallel auth code elsewhere.
- Company and department memberships belong to `accounts`.
- Department membership is the basis for business write permissions.

## 9. API Standard

- Versioned prefix: `/api/v1/`
- JSON-only platform API contract
- Standard response envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

- Business list and detail APIs must follow the same response contract.
- Errors must be normalized through shared exception handling.

## 10. Gateway Role Definition

`gateway` is the platform’s unified API surface.

It should:

- expose platform entrypoints
- advertise available platform modules
- aggregate root-level app URLs
- become the future policy and integration boundary for EAI behavior

It should not become a dumping ground for unrelated business logic.

## 11. AI / MCP Compatibility Rules

- APIs should use stable, explicit, machine-friendly naming.
- Avoid HTML-first assumptions for platform behavior.
- Prefer structured metadata over implicit behavior.
- Discovery endpoints should remain clear enough for AI agents to reason about available capabilities.
- Gateway and service metadata should support future MCP-aligned tool exposure.

## 12. Development Workflow

- Read `AGENTS.md`, this file, and recent `codex-history/` before substantial work.
- Inspect repository state before proposing structural changes.
- Prefer shared abstractions when the same rule applies across multiple apps.
- Use `project.settings.local` explicitly for development workflows.
- Use `project.settings.prod` explicitly for production runtime entrypoints.
- Keep migrations explicit and safe, especially for tenant or auth changes.
- Verify with `python manage.py check`, relevant migrations, and tests after meaningful changes.
- Record significant work in the current month’s history file.

## 13. Safety Rules

- Do not modify `AGENTS.md` unless explicitly instructed.
- Do not delete or clean up history files under `codex-history/`.
- Do not let runtime entrypoints silently fall back to development settings.
- Do not introduce cross-app auth duplication.
- Do not let business data exist without a company owner.
- Non-superusers must not see business data outside their own companies.
- Department-based permissions must be respected for business write operations.
- Avoid destructive repository actions unless explicitly requested.

## 14. Future Refactoring Note

- A future migration to an `apps/` package may be considered later if the repository grows substantially.
- That refactor is explicitly forbidden in the current phase.
- Until an explicit structural migration is approved and executed, root-level apps are mandatory.

## 15. Final Mindset

Work on ThePeach as a platform architect, not a feature-only developer.

Priorities:

- protect stable architecture
- centralize foundational concerns
- preserve tenant boundaries
- keep APIs consistent
- keep the system ready for both human developers and AI/MCP consumers
