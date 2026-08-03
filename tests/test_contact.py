from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.config import Settings


def valid_contact():
    return {"name":"Test Client","email":"client@example.com","service":"FastAPI REST API development","budget":"1000-2500","timeline":"2-4-weeks","subject":"API project inquiry","message":"I would like to discuss a well-scoped API development project.","website":"","consent":True}

async def test_contact_validation(client):
    body = valid_contact(); body["consent"] = False
    assert (await client.post("/api/v1/contact", json=body)).status_code == 422

async def test_contact_honeypot(client):
    body = valid_contact(); body["website"] = "spam.example"
    assert (await client.post("/api/v1/contact", json=body)).status_code == 400

def configure_email(monkeypatch):
    monkeypatch.setattr(app.state.settings, "resend_api_key", "test_api_key")
    monkeypatch.setattr(app.state.settings, "email_from", "Portfolio <sender@example.com>")
    monkeypatch.setattr(app.state.settings, "contact_receiver_email", "owner@example.com")

async def test_contact_success_uses_resend_configuration(client, monkeypatch):
    configure_email(monkeypatch)
    with patch("app.services.email_service.resend.Emails.send_async", new=AsyncMock(return_value={"id": "email-id"})) as send:
        response = await client.post("/api/v1/contact", json=valid_contact())
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Your inquiry was sent successfully.", "data": {"delivery": "sent", "id": "email-id"}}
    params = send.await_args.args[0]
    assert params["to"] == ["owner@example.com"]
    assert params["reply_to"] == "client@example.com"
    assert "Test Client" in params["subject"]

async def test_contact_missing_resend_configuration(client, monkeypatch):
    monkeypatch.setattr(app.state.settings, "resend_api_key", "")
    monkeypatch.setattr(app.state.settings, "email_from", "")
    monkeypatch.setattr(app.state.settings, "contact_receiver_email", "")
    response = await client.post("/api/v1/contact", json=valid_contact())
    assert response.status_code == 503
    assert response.json()["message"] == "Email service is not configured."

async def test_contact_provider_failure_is_safe(client, monkeypatch):
    configure_email(monkeypatch)
    provider = AsyncMock(side_effect=RuntimeError("test_api_key provider details"))
    with patch("app.services.email_service.resend.Emails.send_async", new=provider):
        response = await client.post("/api/v1/contact", json=valid_contact())
    assert response.status_code == 503
    assert "test_api_key" not in response.text

async def test_contact_receiver_is_loaded_from_environment(client, monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "environment_test_key")
    monkeypatch.setenv("EMAIL_FROM", "Portfolio <sender@example.com>")
    monkeypatch.setenv("CONTACT_RECEIVER_EMAIL", "environment-owner@example.com")
    monkeypatch.setattr(app.state, "settings", Settings(_env_file=None))
    with patch("app.services.email_service.resend.Emails.send_async", new=AsyncMock(return_value={"id": "email-id"})) as send:
        response = await client.post("/api/v1/contact", json=valid_contact())
    assert response.status_code == 200
    assert send.await_args.args[0]["to"] == ["environment-owner@example.com"]

async def test_contact_rejects_non_http_attachment(client):
    body = valid_contact(); body["attachment_link"] = "javascript:alert(1)"
    assert (await client.post("/api/v1/contact", json=body)).status_code == 422

def test_smtp_transport_removed():
    import app.services.email_service as email_service
    assert "smtplib" not in email_service.__dict__
