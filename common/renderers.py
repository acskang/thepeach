from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]

        if data is None:
            payload = {
                "success": response.status_code < 400,
                "data": None,
                "error": None if response.status_code < 400 else {},
            }
        elif isinstance(data, dict) and {"success", "data", "error"} <= data.keys():
            payload = data
        elif response.status_code >= 400:
            message = "Request failed."
            code = "validation_error" if response.status_code == 400 else "error"

            if isinstance(data, dict):
                if "detail" in data:
                    message = data["detail"]
                else:
                    first_value = next(iter(data.values()), None)
                    if isinstance(first_value, list) and first_value:
                        message = first_value[0]
            elif isinstance(data, list) and data:
                message = data[0]

            payload = {
                "success": False,
                "data": None,
                "error": {
                    "code": code,
                    "message": message,
                    "details": data,
                },
            }
        else:
            payload = {
                "success": True,
                "data": data,
                "error": None,
            }

        return super().render(payload, accepted_media_type, renderer_context)
