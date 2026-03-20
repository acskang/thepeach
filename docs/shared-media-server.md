# ThePeach Shared Media Server

ThePeach provides a centralized shared image server so multiple Django projects and frontend applications can reuse the same uploaded image URL instead of duplicating files.

## Purpose

- upload an image once
- store it centrally
- return a reusable `file_url`
- let other services consume the file directly from `/media/...`

The consuming service does not need application registration, logo codes, or usage-type knowledge.

## Endpoints

- `POST /api/v1/media/assets/`
- `GET /api/v1/media/assets/`
- `GET /api/v1/media/assets/<id>/`
- `PATCH /api/v1/media/assets/<id>/`
- `POST /api/v1/media/assets/<id>/deactivate/`
- `POST /api/v1/media/assets/<id>/replace/`
- `GET /api/v1/media/assets/by-checksum/<checksum>/`

## Refactor Note

Older logo-specific endpoints and operator pages were replaced by generic shared asset contracts:

- old: `/api/v1/media/logos/`
- new: `/api/v1/media/assets/`

- old operator pages: `/logos/...`
- new operator pages: `/assets/...`

## Upload Constraints

- allowed types: PNG, JPEG
- server-side image validation is mandatory
- corrupted files are rejected
- upload size limit is controlled by `THEPEACH_MEDIA_MAX_UPLOAD_BYTES`

## Response Goal

Upload success returns metadata including:

- `id`
- `file_url`
- `original_file_name`
- `stored_file_name`
- `file_size`
- `mime_type`
- `width`
- `height`
- `checksum_sha256`
- `is_active`

## Deduplication

ThePeach computes `checksum_sha256` on upload.

Current policy:

- if an active asset with the same checksum already exists, the API returns the existing asset instead of creating duplicate storage
- replacement rejects a file that matches a different active asset checksum

## Storage Layout

Files are stored under:

- `media_files/shared/images/YYYY/MM/`

Nginx should serve `MEDIA_URL` directly in production.

## Production Notes

- Cloudflare -> Nginx -> Gunicorn -> Django
- Django handles upload and metadata only
- Nginx serves `/media/`
- uploaded media should be backed up separately from database backups
- file retention should be governed by deactivation and backup policy, not implicit deletion
