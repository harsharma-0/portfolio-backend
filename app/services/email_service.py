import asyncio
import logging
from pathlib import Path
from typing import Any

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import Settings
from app.core.exceptions import EmailConfigurationError, EmailDeliveryError

logger = logging.getLogger(__name__)
templates = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates"),
    autoescape=select_autoescape(["html"]),
)


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def send(
        self,
        template_name: str,
        subject: str,
        context: dict[str, Any],
        reply_to: str | None = None,
    ) -> dict[str, str]:
        if not self.settings.email_configured:
            raise EmailConfigurationError("Email service is not configured")

        rendered_html = templates.get_template(template_name).render(**context)
        resend.api_key = self.settings.resend_api_key
        params: resend.Emails.SendParams = {
            "from": self.settings.email_from,
            "to": [self.settings.contact_receiver_email],
            "subject": subject,
            "html": rendered_html,
        }
        if reply_to:
            params["reply_to"] = reply_to

        try:
            async with asyncio.timeout(15):
                response = await resend.Emails.send_async(params)
        except Exception as exc:
            status = getattr(exc, "code", None)
            logger.warning(
                "Email provider failure type=%s status=%s",
                type(exc).__name__,
                status if isinstance(status, (int, str)) else "unknown",
            )
            raise EmailDeliveryError("Email provider failed") from exc

        provider_id = response.get("id") if isinstance(response, dict) else None
        return {"delivery": "sent", **({"id": str(provider_id)} if provider_id else {})}
