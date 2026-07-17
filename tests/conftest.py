import os
os.environ.update({"APP_ENV": "test", "DEBUG": "false", "SMTP_HOST": "", "SMTP_USERNAME": "", "SMTP_PASSWORD": "", "SMTP_FROM_EMAIL": "", "CONTACT_RECEIVER_EMAIL": ""})

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as api:
        yield api
