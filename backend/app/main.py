from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import (
    FasalSetuException,
    fasalsetu_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
    database_exception_handler,
)
from sqlalchemy.exc import DBAPIError
from app.api.v1.router import api_router
import time
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("FasalSetu API starting", env=settings.app_env)

    # Load AI models at startup (once, not per request)
    from app.ai.disease_detector import DiseaseDetector
    from app.ai.health_classifier import HealthClassifier
    DiseaseDetector.get()    # Loads YOLOv8 ONNX into memory
    HealthClassifier.get()   # Loads EfficientNet ONNX into memory

    yield
    logger.info("FasalSetu API shutting down")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Crop Lifecycle Monitoring & Smart Insurance Verification",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)


def get_allowed_origins() -> list[str]:
    """
    Build allowed origins list.
    In development, allow all localhost ports for Flutter Web compatibility.
    In production, use only the explicit ALLOWED_ORIGINS from .env.
    """
    origins = [o.strip() for o in settings.allowed_origins.split(",")]

    if not settings.is_production:
        # Flutter Web uses a random port - allow all localhost variants
        localhost_origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:5173",   # React dashboard (Vite)
            "http://localhost:3000",   # React dashboard (CRA)
            "http://localhost:8080",   # Flutter Web default
            "http://localhost:64526",  # Flutter Web (common)
            "http://localhost:50000",  # Flutter Web (common)
        ]
        for origin in localhost_origins:
            if origin not in origins:
                origins.append(origin)

    return origins


# CORS — must be before all other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$"
    if not settings.is_production else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
    max_age=3600,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response


app.add_exception_handler(FasalSetuException, fasalsetu_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DBAPIError, database_exception_handler)


app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }

@app.exception_handler(Exception)
async def cors_safe_unhandled_exception_handler(request: Request, exc: Exception):
    """
    Same behavior as unhandled_exception_handler, but guarantees CORS
    headers are present on the response. Without this, an unhandled 500
    on any endpoint (e.g. crop timeline) is delivered without
    Access-Control-Allow-Origin, which Flutter Web's XHR layer reports
    as a generic connection error ("DioException [connection error]")
    instead of a readable 500 — masking the real error.
    """
    response = await unhandled_exception_handler(request, exc)
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
