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
)
from app.api.v1.router import api_router
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("FasalSetu API starting", env=settings.app_env)
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response


# Exception handlers
app.add_exception_handler(FasalSetuException, fasalsetu_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Routers
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }