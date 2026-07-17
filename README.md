# Portfolio API

FastAPI backend for Harsh Vishwakarma's portfolio. Content is read from `app/data/*.json`; only contact inquiries and project feedback leave the application, through SMTP. Nothing is stored.

## Commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
pytest
```

All public endpoints use `/api/v1`. Interactive documentation is available at `/docs` and `/redoc`. Configure SMTP and frontend origins in `.env`; do not commit that file.

For production, set `APP_ENV=production`, `DEBUG=false`, and exact allowed frontend origins. Development email fallback is intentionally unavailable in production. Keep SMTP credentials in server environment configuration, never frontend files or JSON content.
