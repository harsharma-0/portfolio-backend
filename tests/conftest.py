import os
os.environ.update({"APP_ENV": "test", "DEBUG": "false", "RESEND_API_KEY": "", "EMAIL_FROM": "", "CONTACT_RECEIVER_EMAIL": ""})

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as api:
        yield api
