from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import reject_header_injection, validate_http_url


class Budget(str, Enum):
    under_500 = "under-500"
    from_500_1000 = "500-1000"
    from_1000_2500 = "1000-2500"
    from_2500_5000 = "2500-5000"
    above_5000 = "5000-plus"
    discuss = "discuss"


class Timeline(str, Enum):
    urgent = "urgent"
    one_two_weeks = "1-2-weeks"
    two_four_weeks = "2-4-weeks"
    one_three_months = "1-3-months"
    flexible = "flexible"


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    service: str = Field(min_length=2, max_length=100)
    budget: Budget
    timeline: Timeline
    subject: str = Field(min_length=5, max_length=120)
    message: str = Field(min_length=20, max_length=3000)
    attachment_link: str | None = None
    website: str = Field(default="", max_length=200)
    consent: bool

    @field_validator("name", "service", "subject", "message", mode="before")
    @classmethod
    def clean_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("name", "subject")
    @classmethod
    def safe_headers(cls, value: str) -> str:
        return reject_header_injection(value)

    @field_validator("attachment_link")
    @classmethod
    def attachment_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @field_validator("consent")
    @classmethod
    def consent_required(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Consent is required")
        return value
