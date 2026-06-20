# from fastapi import APIRouter
# from app.api.v1.routes import auth, farms, crops, images, claims, advisories, fraud, admin

# api_router = APIRouter(prefix="/api/v1")

# api_router.include_router(auth.router,        prefix="/auth",       tags=["Authentication"])
# api_router.include_router(farms.router,       prefix="/farms",      tags=["Farms"])
# api_router.include_router(crops.router,       prefix="/crops",      tags=["Crop Lifecycle"])
# api_router.include_router(images.router,      prefix="/images",     tags=["Images"])
# api_router.include_router(claims.router,      prefix="/claims",     tags=["Claims"])
# api_router.include_router(advisories.router,  prefix="/advisories", tags=["Advisories"])
# api_router.include_router(fraud.router,       prefix="/fraud",      tags=["Fraud & Trust"])
# api_router.include_router(admin.router,       prefix="/admin",      tags=["Admin"])

from fastapi import APIRouter
from app.api.v1.routes import (
    auth, farms, crops, images, claims, advisories, fraud, admin
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router,       prefix="/auth",       tags=["Authentication"])
api_router.include_router(farms.router,      prefix="/farms",      tags=["Farms"])
api_router.include_router(crops.router,      prefix="/crops",      tags=["Crop Lifecycle"])
api_router.include_router(images.router,     prefix="/images",     tags=["Images"])
api_router.include_router(claims.router,     prefix="/claims",     tags=["Claims"])
api_router.include_router(advisories.router, prefix="/advisories", tags=["Advisories"])
api_router.include_router(fraud.router,      prefix="/fraud",      tags=["Fraud & Trust"])
api_router.include_router(admin.router,      prefix="/admin",      tags=["Admin"])