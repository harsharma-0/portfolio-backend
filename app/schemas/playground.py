from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class TextAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)


class JsonInspectorRequest(BaseModel):
    payload: dict[str, Any] | list[Any]


class DataTransformRequest(BaseModel):
    items: list[dict[str, Any]] = Field(min_length=0, max_length=500)
    search: str = Field(default="", max_length=100)
    category: str = Field(default="", max_length=100)
    sort_by: Literal["name", "category", "score"] = "score"
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=5, ge=1, le=100)

    @field_validator("items")
    @classmethod
    def validate_items(cls, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for item in items:
            if not {"name", "category", "score"}.issubset(item):
                raise ValueError("Each item requires name, category and score")
            if not isinstance(item["name"], str) or not isinstance(item["category"], str) or not isinstance(item["score"], (int, float)) or isinstance(item["score"], bool):
                raise ValueError("Item fields have invalid types")
        return items
