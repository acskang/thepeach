import logging
import json
from urllib import error, parse, request
from urllib.parse import urlparse

from django.conf import settings

from core.exceptions import ThePeachAuthContractError, ThePeachAuthUnavailable

from .models import ThePeachAuthContext, ThePeachRemoteUser

auth_logger = logging.getLogger("trusted_portal.auth")


class ThePeachAuthClient:
    """
    The new service trusts ThePeach's auth API as the authentication source of truth.
    It only normalizes the remote payload into a request-friendly shape.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        auth_login_path: str | None = None,
        auth_me_path: str | None = None,
        timeout_seconds: float | None = None,
        forward_headers: list[str] | None = None,
    ):
        self.base_url = (base_url or settings.THEPEACH_BASE_URL).rstrip("/")
        self.fallback_base_urls = [(item or "").rstrip("/") for item in settings.THEPEACH_FALLBACK_BASE_URLS]
        self.auth_login_path = auth_login_path or settings.THEPEACH_AUTH_LOGIN_PATH
        self.auth_me_path = auth_me_path or settings.THEPEACH_AUTH_ME_PATH
        self.timeout_seconds = timeout_seconds or settings.THEPEACH_AUTH_TIMEOUT_SECONDS
        self.forward_headers = [header.lower() for header in (forward_headers or settings.THEPEACH_FORWARD_HEADERS)]

    def login(
        self,
        *,
        email: str,
        password: str,
        request_headers: dict[str, str] | None = None,
        request_host: str = "",
    ) -> dict:
        candidates = self._candidate_base_urls(request_host=request_host)
        last_http_404 = None
        auth_logger.info(
            "relay_login_started email=%s request_host=%s candidates=%s",
            email,
            request_host or "-",
            ",".join(candidates),
        )
        for base_url in candidates:
            try:
                payload, _status_code, response_headers = self._post_login(
                    base_url=base_url,
                    email=email,
                    password=password,
                    request_headers=request_headers or {},
                )
                auth_logger.info(
                    "relay_login_succeeded email=%s upstream=%s upstream_request_id=%s",
                    email,
                    base_url,
                    response_headers.get("x-request-id", "-"),
                )
                return self._validate_login_payload(payload)
            except error.HTTPError as exc:
                error_body = self._read_http_error_body(exc)
                auth_logger.warning(
                    "relay_login_http_error email=%s upstream=%s status=%s body=%s",
                    email,
                    base_url,
                    exc.code,
                    error_body,
                )
                if exc.code == 404:
                    last_http_404 = exc
                    continue
                if exc.code in {400, 401, 403}:
                    edge_block_message = self._extract_edge_block_message(error_body, status_code=exc.code)
                    if edge_block_message:
                        raise ThePeachAuthContractError(edge_block_message)
                    try:
                        payload = json.loads(error_body) if error_body and error_body != "<empty>" else {}
                    except json.JSONDecodeError:
                        payload = {}
                    message = self._extract_error_message(payload) or "ThePeach rejected the supplied credentials."
                    raise ThePeachAuthContractError(message)
                if 500 <= exc.code <= 599:
                    raise ThePeachAuthUnavailable("ThePeach auth service returned a server error.") from exc
                raise ThePeachAuthContractError(f"Unexpected response from ThePeach auth service: HTTP {exc.code}.") from exc
            except error.URLError as exc:
                auth_logger.error(
                    "relay_login_transport_error email=%s upstream=%s reason=%s",
                    email,
                    base_url,
                    exc.reason,
                )
                raise ThePeachAuthUnavailable(f"Unable to reach ThePeach auth service: {exc.reason}") from exc
            except TimeoutError as exc:
                auth_logger.error(
                    "relay_login_timeout email=%s upstream=%s",
                    email,
                    base_url,
                )
                raise ThePeachAuthUnavailable("ThePeach auth service timed out.") from exc

        tried = ", ".join(candidates)
        auth_logger.error("relay_login_endpoint_missing email=%s tried=%s", email, tried)
        raise ThePeachAuthContractError(
            f"ThePeach auth login endpoint was not found. Tried: {tried}."
        ) from last_http_404

    def authenticate(
        self,
        *,
        access_token: str,
        request_headers: dict[str, str] | None = None,
        request_host: str = "",
    ) -> ThePeachAuthContext:
        if not access_token:
            return ThePeachAuthContext(
                is_authenticated=False,
                status_code=None,
                source="missing_token",
                error_code="missing_token",
                error_message="No ThePeach access token was provided.",
            )

        candidates = self._candidate_base_urls(request_host=request_host)
        last_http_404 = None
        auth_logger.info(
            "profile_auth_started request_host=%s candidates=%s",
            request_host or "-",
            ",".join(candidates),
        )
        for base_url in candidates:
            try:
                payload, status_code, response_headers = self._fetch_profile(
                    base_url=base_url,
                    access_token=access_token,
                    request_headers=request_headers or {},
                )
                self._validate_profile_payload(payload)
                data = payload.get("data")
                user = self._normalize_user(data)
                if not user.is_active:
                    return ThePeachAuthContext(
                        is_authenticated=False,
                        status_code=status_code,
                        source="thepeach_api",
                        error_code="inactive_user",
                        error_message="ThePeach user is inactive.",
                    )

                auth_logger.info(
                    "profile_auth_succeeded upstream=%s status=%s upstream_request_id=%s user_id=%s",
                    base_url,
                    status_code,
                    response_headers.get("x-request-id", "-"),
                    user.id,
                )
                return ThePeachAuthContext(
                    is_authenticated=True,
                    status_code=status_code,
                    source="thepeach_api",
                    user=user,
                    access_token=access_token,
                )
            except error.HTTPError as exc:
                error_body = self._read_http_error_body(exc)
                auth_logger.warning(
                    "profile_auth_http_error upstream=%s status=%s body=%s",
                    base_url,
                    exc.code,
                    error_body,
                )
                if exc.code == 404:
                    last_http_404 = exc
                    continue
                return self._from_http_error(exc)
            except error.URLError as exc:
                auth_logger.error(
                    "profile_auth_transport_error upstream=%s reason=%s",
                    base_url,
                    exc.reason,
                )
                raise ThePeachAuthUnavailable(f"Unable to reach ThePeach auth service: {exc.reason}") from exc
            except TimeoutError as exc:
                auth_logger.error("profile_auth_timeout upstream=%s", base_url)
                raise ThePeachAuthUnavailable("ThePeach auth service timed out.") from exc

        tried = ", ".join(candidates)
        auth_logger.error("profile_auth_endpoint_missing tried=%s", tried)
        raise ThePeachAuthContractError(
            f"ThePeach auth profile endpoint was not found. Tried: {tried}."
        ) from last_http_404

    def _fetch_profile(self, *, base_url: str, access_token: str, request_headers: dict[str, str]) -> tuple[dict, int, dict]:
        url = parse.urljoin(f"{base_url}/", self.auth_me_path.lstrip("/"))
        headers = {"Authorization": f"Bearer {access_token}"}
        for header_name, value in request_headers.items():
            if header_name.lower() in self.forward_headers and value:
                headers[header_name] = value
        auth_request = request.Request(url, headers=headers, method="GET")
        with request.urlopen(auth_request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
            return json.loads(body), response.status, dict(response.headers.items())

    def _post_login(self, *, base_url: str, email: str, password: str, request_headers: dict[str, str]) -> tuple[dict, int, dict]:
        url = parse.urljoin(f"{base_url}/", self.auth_login_path.lstrip("/"))
        headers = {"Content-Type": "application/json"}
        for header_name, value in request_headers.items():
            if header_name.lower() in self.forward_headers and value:
                headers[header_name] = value
        body = json.dumps({"email": email, "password": password}).encode("utf-8")
        login_request = request.Request(url, headers=headers, data=body, method="POST")
        with request.urlopen(login_request, timeout=self.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload), response.status, dict(response.headers.items())

    def _candidate_base_urls(self, *, request_host: str) -> list[str]:
        candidates = [self.base_url]
        candidates.extend([item for item in self.fallback_base_urls if item])

        host_candidate = self._derive_local_fallback_url(request_host=request_host)
        if host_candidate:
            candidates.append(host_candidate)

        deduped = []
        seen = set()
        for item in candidates:
            normalized = item.rstrip("/")
            if not normalized or normalized in seen:
                continue
            deduped.append(normalized)
            seen.add(normalized)
        return deduped

    def _derive_local_fallback_url(self, *, request_host: str) -> str:
        if not request_host:
            return ""
        parsed = urlparse(f"http://{request_host}")
        hostname = parsed.hostname or ""
        port = parsed.port
        if hostname not in {"localhost", "127.0.0.1"} or port not in {8000, 8001}:
            return ""
        alternate_port = 8001 if port == 8000 else 8000
        return f"http://{hostname}:{alternate_port}"

    def _from_http_error(self, exc: error.HTTPError) -> ThePeachAuthContext:
        status_code = exc.code
        if status_code in {401, 403}:
            return ThePeachAuthContext(
                is_authenticated=False,
                status_code=status_code,
                source="thepeach_api",
                error_code="invalid_token" if status_code == 401 else "forbidden",
                error_message="ThePeach rejected the supplied access token.",
            )
        if 500 <= status_code <= 599:
            raise ThePeachAuthUnavailable("ThePeach auth service returned a server error.") from exc
        raise ThePeachAuthContractError(f"Unexpected response from ThePeach auth service: HTTP {status_code}.") from exc

    def _normalize_user(self, data: dict) -> ThePeachRemoteUser:
        return ThePeachRemoteUser(
            id=str(data.get("id", "")),
            email=data.get("email", ""),
            full_name=data.get("full_name", ""),
            display_name=data.get("display_name") or data.get("full_name", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            smartphone_number=data.get("smartphone_number", ""),
            external_id=data.get("external_id", ""),
            companies=self._normalize_companies(data.get("companies")),
            departments=self._normalize_departments(data.get("departments")),
            is_active=bool(data.get("is_active", True)),
            raw=data,
        )

    def _normalize_companies(self, items) -> list[dict]:
        if not isinstance(items, list):
            return []
        normalized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "id": str(item.get("id", "")),
                    "name": item.get("name", ""),
                    "code": item.get("code", ""),
                    "is_active": bool(item.get("is_active", True)),
                }
            )
        return normalized

    def _extract_error_message(self, payload: dict) -> str:
        error_payload = payload.get("error")
        if isinstance(error_payload, dict) and error_payload.get("message"):
            return str(error_payload["message"])
        return ""

    def _validate_login_payload(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            raise ThePeachAuthContractError("ThePeach auth service returned a non-object response.")
        if payload.get("success") is not True or not isinstance(payload.get("data"), dict):
            raise ThePeachAuthContractError(self._extract_error_message(payload) or "ThePeach login response was invalid.")
        return payload["data"]

    def _validate_profile_payload(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ThePeachAuthContractError("ThePeach auth service returned a non-object response.")
        data = payload.get("data")
        if payload.get("success") is not True or not isinstance(data, dict):
            raise ThePeachAuthContractError("ThePeach auth service returned an unexpected success payload.")

    def _read_http_error_body(self, exc: error.HTTPError) -> str:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            return "<unreadable>"
        return body[:1000] if body else "<empty>"

    def _extract_edge_block_message(self, body: str, *, status_code: int) -> str:
        normalized_body = (body or "").lower()
        if status_code == 403 and "error code: 1010" in normalized_body:
            return (
                "ThePeach edge denied this server-side login relay (Cloudflare 1010). "
                "Direct browser login to thepeach.thesysm.com may still work."
            )
        return ""

    def _normalize_departments(self, items) -> list[dict]:
        if not isinstance(items, list):
            return []
        normalized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            company = item.get("company") if isinstance(item.get("company"), dict) else {}
            normalized.append(
                {
                    "id": str(item.get("id", "")),
                    "name": item.get("name", ""),
                    "code": item.get("code", ""),
                    "is_active": bool(item.get("is_active", True)),
                    "company": {
                        "id": str(company.get("id", "")),
                        "name": company.get("name", ""),
                        "code": company.get("code", ""),
                        "is_active": bool(company.get("is_active", True)),
                    },
                }
            )
        return normalized
