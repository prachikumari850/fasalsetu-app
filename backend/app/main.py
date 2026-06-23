# # from fastapi import FastAPI, Request
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.exceptions import RequestValidationError
# # from contextlib import asynccontextmanager
# # from app.core.config import settings
# # from app.core.logging import setup_logging, logger
# # from app.core.exceptions import (
# #     FasalSetuException,
# #     fasalsetu_exception_handler,
# #     validation_exception_handler,
# #     unhandled_exception_handler,
# # )
# # from app.api.v1.router import api_router
# # import time


# # @asynccontextmanager
# # async def lifespan(app: FastAPI):
# #     setup_logging()
# #     logger.info("FasalSetu API starting", env=settings.app_env)
# #     yield
# #     logger.info("FasalSetu API shutting down")


# # app = FastAPI(
# #     title=settings.app_name,
# #     version=settings.app_version,
# #     description="AI-Powered Crop Lifecycle Monitoring & Smart Insurance Verification",
# #     docs_url="/docs" if not settings.is_production else None,
# #     redoc_url="/redoc" if not settings.is_production else None,
# #     lifespan=lifespan,
# # )

# # # CORS
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=settings.origins_list,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )


# # # Request timing middleware
# # @app.middleware("http")
# # async def add_process_time_header(request: Request, call_next):
# #     start = time.time()
# #     response = await call_next(request)
# #     response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
# #     return response


# # # Exception handlers
# # app.add_exception_handler(FasalSetuException, fasalsetu_exception_handler)
# # app.add_exception_handler(RequestValidationError, validation_exception_handler)
# # app.add_exception_handler(Exception, unhandled_exception_handler)

# # # Routers
# # app.include_router(api_router)


# # @app.get("/health", tags=["Health"])
# # async def health_check():
# #     return {
# #         "status": "healthy",
# #         "app": settings.app_name,
# #         "version": settings.app_version,
# #         "env": settings.app_env,
# #     }

# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError
# from contextlib import asynccontextmanager
# from app.core.config import settings
# from app.core.logging import setup_logging, logger
# from app.core.exceptions import (
#     FasalSetuException,
#     fasalsetu_exception_handler,
#     validation_exception_handler,
#     unhandled_exception_handler,
# )
# from app.api.v1.router import api_router
# import time
# import re


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     setup_logging()
#     logger.info("FasalSetu API starting", env=settings.app_env)
#     yield
#     logger.info("FasalSetu API shutting down")


# app = FastAPI(
#     title=settings.app_name,
#     version=settings.app_version,
#     description="AI-Powered Crop Lifecycle Monitoring & Smart Insurance Verification",
#     docs_url="/docs" if not settings.is_production else None,
#     redoc_url="/redoc" if not settings.is_production else None,
#     lifespan=lifespan,
# )


# def get_allowed_origins() -> list[str]:
#     """
#     Build allowed origins list.
#     In development, allow all localhost ports for Flutter Web compatibility.
#     In production, use only the explicit ALLOWED_ORIGINS from .env.
#     """
#     origins = [o.strip() for o in settings.allowed_origins.split(",")]

#     if not settings.is_production:
#         # Flutter Web uses a random port - allow all localhost variants
#         localhost_origins = [
#             "http://localhost",
#             "http://127.0.0.1",
#             "http://localhost:5173",   # React dashboard (Vite)
#             "http://localhost:3000",   # React dashboard (CRA)
#             "http://localhost:8080",   # Flutter Web default
#             "http://localhost:64526",  # Flutter Web (common)
#             "http://localhost:50000",  # Flutter Web (common)
#         ]
#         for origin in localhost_origins:
#             if origin not in origins:
#                 origins.append(origin)

#     return origins


# # CORS — must be before all other middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=get_allowed_origins(),
#     allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$"
#     if not settings.is_production else None,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
#     expose_headers=["X-Process-Time"],
#     max_age=3600,
# )


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start = time.time()
#     response = await call_next(request)
#     response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
#     return response


# app.add_exception_handler(FasalSetuException, fasalsetu_exception_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
# app.add_exception_handler(Exception, unhandled_exception_handler)

# app.include_router(api_router)


# @app.get("/health", tags=["Health"])
# async def health_check():
#     return {
#         "status": "healthy",
#         "app": settings.app_name,
#         "version": settings.app_version,
#         "env": settings.app_env,
#     }

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

    # Load AI models at startup (once, not per request)
    try:
        from app.ai.disease_detector import DiseaseDetector
        from app.ai.health_classifier import HealthClassifier
        DiseaseDetector.get()
        HealthClassifier.get()
    except Exception as e:
        logger.warning("AI models not loaded", error=str(e))

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

# ── CORS ──────────────────────────────────────────────────────────────────────
# Flutter Web uses a RANDOM port on every `flutter run` invocation.
# We must allow ALL localhost ports — not just specific ones.
# allow_origin_regex handles this without listing every possible port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # React dashboard (Vite)
        "http://localhost:3000",   # React dashboard (CRA)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    # This regex allows Flutter Web on ANY localhost port (53523, 8090, etc.)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$",
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
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status":  "healthy",
        "app":     settings.app_name,
        "version": settings.app_version,
        "env":     settings.app_env,
    }