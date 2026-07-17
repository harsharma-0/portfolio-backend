import re
from urllib.parse import urlparse


HEADER_INJECTION = re.compile(r"[\r\n]")


def reject_header_injection(value: str) -> str:
    if HEADER_INJECTION.search(value):
        raise ValueError("Newline characters are not allowed")
    return value.strip()


def validate_http_url(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Attachment link must be a valid HTTP or HTTPS URL")
    return cleaned
