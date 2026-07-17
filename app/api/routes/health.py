from datetime import datetime, timezone
from fastapi import APIRouter, Request
from app.schemas.common import success

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health(request: Request):
    settings = request.app.state.settings
    return success("API is healthy", {"application": settings.app_name, "status": "healthy", "api_version": settings.app_version, "environment": settings.app_env, "timestamp": datetime.now(timezone.utc).isoformat()})
