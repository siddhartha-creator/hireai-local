from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    data: Any | None = None
    message: str = "Success"
    request_id: str | None = None
    errors: list[dict] | None = None
