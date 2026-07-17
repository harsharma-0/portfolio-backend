import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.router import api_router
from app.api.routes.contact import limiter
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

settings = get_settings(); configure_logging(settings.debug); logger = logging.getLogger("app.request")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s %s (%s)", settings.app_name, settings.app_version, settings.app_env)
    yield
    logger.info("Application stopped")

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug, lifespan=lifespan)
app.state.settings = settings; app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, __: RateLimitExceeded):
    return JSONResponse(429, {"success": False, "message": "Too many requests; please try again later", "errors": {}})

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Accept"])

@app.middleware("http")
async def protections(request: Request, call_next):
    started = time.perf_counter()
    if request.method in {"POST", "PUT", "PATCH"}:
        if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
            return JSONResponse(415, {"success": False, "message": "Content-Type must be application/json", "errors": {}})
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > settings.max_request_bytes:
            return JSONResponse(413, {"success": False, "message": "Request body is too large", "errors": {}})
    response = await call_next(request)
    response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "strict-origin-when-cross-origin", "Permissions-Policy": "camera=(), microphone=(), geolocation=()"})
    logger.info("method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)

@app.get("/", include_in_schema=False)
async def root(): return {"success": True, "message": settings.app_name, "data": {"docs": "/docs", "health": f"{settings.api_prefix}/health"}}
