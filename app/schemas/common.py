from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T


def success(message: str, data: Any) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}
