from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DBAPIError, OperationalError
import structlog

logger = structlog.get_logger()


class FasalSetuException(Exception):
    def __init__(self, status_code: int, detail: str, code: str = "ERROR"):
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(detail)


class NotFoundException(FasalSetuException):
    def __init__(self, resource: str):
        super().__init__(404, f"{resource} not found", "NOT_FOUND")


class ForbiddenException(FasalSetuException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(403, detail, "FORBIDDEN")


class UnauthorizedException(FasalSetuException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(401, detail, "UNAUTHORIZED")


class ValidationException(FasalSetuException):
    def __init__(self, detail: str):
        super().__init__(422, detail, "VALIDATION_ERROR")


class ConflictException(FasalSetuException):
    def __init__(self, detail: str):
        super().__init__(409, detail, "CONFLICT")


class ServiceUnavailableException(FasalSetuException):
    def __init__(self, detail: str = "The data service is temporarily unavailable"):
        super().__init__(503, detail, "SERVICE_UNAVAILABLE")


async def fasalsetu_exception_handler(
    request: Request, exc: FasalSetuException
) -> JSONResponse:
    logger.warning(
        "Application error",
        code=exc.code,
        detail=exc.detail,
        path=str(request.url),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "detail": exc.detail, "success": False},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    logger.warning("Validation error", errors=errors, path=str(request.url))
    return JSONResponse(
        status_code=422,
        content={"code": "VALIDATION_ERROR", "detail": errors, "success": False},
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error(
        "Unhandled exception",
        exc_type=type(exc).__name__,
        detail=str(exc),
        path=str(request.url),
    )
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred",
            "success": False,
        },
    )


async def database_exception_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    """Keep database credentials/driver details out of API responses."""
    logger.error(
        "Database operation failed",
        exc_type=type(exc).__name__,
        detail=str(exc),
        path=str(request.url),
    )
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "code": "DATABASE_UNAVAILABLE",
            "detail": "The data service is temporarily unavailable. Please try again.",
        },
    )
