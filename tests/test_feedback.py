from unittest.mock import AsyncMock, patch

from app.main import app


async def test_feedback_validation(client):
    response = await client.post("/api/v1/feedback", json={"name":"A","project_slug":"bad slug","feedback_type":"wrong","message":"short"})
    assert response.status_code == 422

async def test_invalid_project_feedback(client):
    response = await client.post("/api/v1/feedback", json={"name":"Test User","project_slug":"missing-project","feedback_type":"comment","message":"This is thoughtful project feedback."})
    assert response.status_code == 404

async def test_feedback_success_uses_resend(client, monkeypatch):
    monkeypatch.setattr(app.state.settings, "resend_api_key", "test_api_key")
    monkeypatch.setattr(app.state.settings, "email_from", "Portfolio <sender@example.com>")
    monkeypatch.setattr(app.state.settings, "contact_receiver_email", "feedback-owner@example.com")
    body = {"name":"Test User","email":"test@example.com","project_slug":"aws-cost-calculator","feedback_type":"appreciation","message":"The cost-estimation architecture is thoughtfully presented."}
    with patch("app.services.email_service.resend.Emails.send_async", new=AsyncMock(return_value={"id": "feedback-id"})) as send:
        response = await client.post("/api/v1/feedback", json=body)
    assert response.status_code == 200
    assert response.json()["data"]["delivery"] == "sent"
    params = send.await_args.args[0]
    assert params["to"] == ["feedback-owner@example.com"]
    assert params["reply_to"] == "test@example.com"
    assert "aws-cost-calculator" in params["subject"]
