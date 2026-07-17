import asyncio
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import Settings

logger = logging.getLogger(__name__)
templates = Environment(loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates"), autoescape=select_autoescape(["html"]))


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def send(self, template_name: str, subject: str, context: dict[str, Any], reply_to: str | None = None) -> str:
        html = templates.get_template(template_name).render(**context)
        if not self.settings.smtp_configured:
            if self.settings.app_env.casefold() in {"development", "local", "test", "testing"}:
                logger.info("SMTP disabled; development email preview type=%s subject=%s", template_name, escape(subject))
                return "development"
            raise RuntimeError("Email delivery is not configured")
        await asyncio.to_thread(self._send_sync, subject, html, reply_to)
        return "sent"

    def _send_sync(self, subject: str, html: str, reply_to: str | None) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = formataddr((self.settings.smtp_from_name, self.settings.smtp_from_email))
        message["To"] = self.settings.contact_receiver_email
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content("This message requires an HTML-capable email client.")
        message.add_alternative(html, subtype="html")
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)
