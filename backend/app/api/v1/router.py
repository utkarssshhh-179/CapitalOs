from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.borrower.router import router as borrower_router
from app.modules.health.router import router as health_router
from app.modules.investor.router import router as investor_router
from app.modules.organization.router import router as organization_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(organization_router)
api_router.include_router(auth_router)
api_router.include_router(borrower_router)
api_router.include_router(investor_router)
# Later milestones register their module routers here.
