from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import reject_header_injection


class FeedbackType(str, Enum):
    comment = "comment"
    appreciation = "appreciation"
    inquiry = "project-inquiry"


class FeedbackRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr | None = None
    project_slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9-]+$")
    feedback_type: FeedbackType
    message: str = Field(min_length=10, max_length=2000)
    website: str = Field(default="", max_length=200)

    @field_validator("name", "project_slug", "message", mode="before")
    @classmethod
    def trim(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("name")
    @classmethod
    def safe_name(cls, value: str) -> str:
        return reject_header_injection(value)
