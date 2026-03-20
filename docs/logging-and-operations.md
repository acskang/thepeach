# Logging And Operations

## Operational Logging

ThePeach maintains operational logging for:

- API requests
- authentication events
- system-level events
- shared media actions

## File-Compatible Logging

Production logging must remain compatible with filesystem-backed log handling so Nginx, Gunicorn, and host-level operations can manage log collection safely.

## Backups

Backups should include both:

- PostgreSQL data
- uploaded files under `media_files/`

## Rollback

Rollback should prefer:

1. restoring the previous release
2. validating service health
3. reversing migrations only when the schema change is confirmed as the failure source

## Observability Mindset

Production behavior should be explainable from logs and operational documents, not reconstructed from guesswork.
