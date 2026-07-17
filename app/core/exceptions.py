import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = {".".join(str(part) for part in error["loc"] if part != "body"): error["msg"] for error in exc.errors()}
        return JSONResponse(status_code=422, content={"success": False, "message": "Request validation failed", "errors": errors})

    @app.exception_handler(HTTPException)
    async def http_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        message = detail if isinstance(detail, str) else "Request could not be completed"
        errors = {} if isinstance(detail, str) else detail
        return JSONResponse(status_code=exc.status_code, content={"success": False, "message": message, "errors": errors})

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"success": False, "message": "An unexpected error occurred", "errors": {}})
