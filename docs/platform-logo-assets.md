# ThePeach Platform Logo Assets

## Purpose

`PlatformLogoAsset` is the central source of truth for reusable logo images linked to registered application services.

This is platform governance data, not a local-only upload helper.

## Relationship To Registered Applications

- every logo is linked to a `RegisteredApplication`
- application lookup uses stable `app_code`
- active logo assets can be queried per application
- usage is explicitly classified by `usage_type`

Current usage types:

- `primary`
- `header`
- `icon`
- `dark_mode`
- `light_mode`

## API Summary

- `POST /api/v1/media/logos/`
- `GET /api/v1/media/logos/`
- `GET /api/v1/media/logos/<id>/`
- `PATCH /api/v1/media/logos/<id>/`
- `POST /api/v1/media/logos/<id>/deactivate/`
- `POST /api/v1/media/logos/<id>/replace/`
- `GET /api/v1/media/logos/by-application/<app_code>/`

## Request Examples

Create logo upload:

```http
POST /api/v1/media/logos/
Authorization: Bearer <access-token>
Content-Type: multipart/form-data
```

Fields:

- `application_code`
- `logo_code`
- `logo_name`
- `usage_type`
- `alt_text`
- `image_file`

Metadata update:

```json
{
  "logo_name": "Updated Header Logo",
  "usage_type": "header",
  "alt_text": "Updated brand header logo"
}
```

## Response Contract

Success:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "validation_error",
    "message": "Human-readable message",
    "details": {}
  }
}
```

## Allowed File Types And Limits

Current phase policy:

- PNG
- JPEG
- max size: `THEPEACH_LOGO_MAX_UPLOAD_BYTES` (default 5 MB)

Corrupted or non-image payloads are rejected server-side.

## Storage Notes

Logo files are stored under:

- `media_files/logos/<application_code>/...`

Filenames are normalized and suffixed with a UUID to reduce collisions.

## Production Notes

- Django stores files under `MEDIA_ROOT`
- Nginx should serve `MEDIA_URL` directly
- Gunicorn serves the API and template screens only
- Cloudflare and Nginx remain in front of Django
- uploads and state-changing operations are logged through the platform logging stack
