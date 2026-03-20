# ThePeach Platform Documentation System

## Overview

The documentation portal is driven by:

- repository markdown files under `docs/`
- an explicit document registry in code
- safe slug-based routing under `/docs/<slug>/`

## Registry

The registry defines:

- slug
- title
- source file path
- summary
- category
- audience
- ordering and related-document metadata

Do not rely on implicit directory scans alone for published documents.

## Adding A New Document

1. add a markdown file under `docs/`
2. add a registry entry in `common/docs_registry.py`
3. choose a stable slug
4. assign category, audience, summary, and ordering
5. add related slugs if helpful
6. verify `/docs/` and `/docs/<slug>/`

## Slug Mapping

Slug mapping is explicit. A slug only resolves if it exists in the registry and points to an actual markdown file.

This prevents:

- ambiguous routes
- arbitrary filesystem access
- dead links

## Renderer

Markdown is rendered from repository files and escaped before conversion so raw HTML is not trusted.

Supported formatting includes:

- headings
- lists
- fenced code blocks
- tables

## Avoiding Dead Links

- keep registry entries synchronized with real files
- remove or fix entries when documents move
- prefer explicit related links over ad hoc inline references
