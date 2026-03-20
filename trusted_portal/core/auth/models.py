from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ThePeachRemoteUser:
    id: str
    email: str
    full_name: str
    display_name: str
    first_name: str
    last_name: str
    smartphone_number: str
    external_id: str
    companies: list[dict[str, Any]] = field(default_factory=list)
    departments: list[dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def company_ids(self) -> list[str]:
        return [item["id"] for item in self.companies if item.get("id")]

    @property
    def department_ids(self) -> list[str]:
        return [item["id"] for item in self.departments if item.get("id")]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "smartphone_number": self.smartphone_number,
            "external_id": self.external_id,
            "companies": self.companies,
            "departments": self.departments,
            "company_ids": self.company_ids,
            "department_ids": self.department_ids,
            "is_active": self.is_active,
        }


@dataclass(slots=True)
class ThePeachAuthContext:
    is_authenticated: bool
    status_code: int | None
    source: str
    user: ThePeachRemoteUser | None = None
    access_token: str = ""
    error_code: str = ""
    error_message: str = ""
