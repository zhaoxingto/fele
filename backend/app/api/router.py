from fastapi import APIRouter

from app.api.routes.company import router as company_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.route import router as route_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(company_router, prefix="/company", tags=["company"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(route_router, prefix="/route", tags=["route"])
