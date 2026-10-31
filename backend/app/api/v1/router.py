from fastapi import APIRouter

from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.borrower.router import router as borrower_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.document.router import router as document_router
from app.modules.health.router import router as health_router
from app.modules.investor.router import router as investor_router
from app.modules.loan.router import router as loan_router
from app.modules.organization.router import router as organization_router
from app.modules.payment.router import router as payment_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(organization_router)
api_router.include_router(auth_router)
api_router.include_router(borrower_router)
api_router.include_router(investor_router)
api_router.include_router(loan_router)
api_router.include_router(payment_router)
api_router.include_router(dashboard_router)
api_router.include_router(ai_router)
api_router.include_router(document_router)
# Later milestones register their module routers here.
