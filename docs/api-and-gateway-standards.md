# API And Gateway Standards

## API Contract

All platform APIs follow the standard response envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

## Error Contract

Errors must remain explicit and stable:

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

## Versioning

ThePeach uses `/api/v1/` as the stable platform prefix.

## Gateway Role

`gateway` is the integration boundary. It should:

- expose top-level discovery
- keep contracts machine-friendly
- avoid domain business logic
- support deterministic routing behavior

## Integration Expectations

Platform APIs are intended for:

- operator tooling
- internal service integration
- future AI and MCP-style callers
