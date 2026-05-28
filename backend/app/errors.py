from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | list[Any] | str | None = field(default=None)

    def to_response(self, request_id: str | None = None) -> dict[str, Any]:
        error: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details is not None:
            error["details"] = self.details
        if request_id is not None:
            error["request_id"] = request_id
        return {"error": error}
