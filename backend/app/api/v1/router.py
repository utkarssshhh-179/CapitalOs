from fastapi import APIRouter

from app.modules.ai.router import router as ai_router
from app.modules.audit_log.router import router as audit_log_router
from app.modules.auth.router import router as auth_router
from app.modules.borrower.router import router as borrower_router
from app.modules.collection.router import router as collection_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.document.router import router as document_router
from app.modules.health.router import router as health_router
from app.modules.investor.router import router as investor_router
from app.modules.ledger.router import router as ledger_router
from app.modules.loan.router import router as loan_router
from app.modules.loan_schedule.router import router as loan_schedule_router
from app.modules.loan_servicing.router import router as loan_servicing_router
from app.modules.organization.router import router as organization_router
from app.modules.payment.router import router as payment_router
from app.modules.reports.router import router as reports_router
from app.modules.underwriting.router import router as underwriting_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(organization_router)
api_router.include_router(auth_router)
api_router.include_router(audit_log_router)
api_router.include_router(borrower_router)
api_router.include_router(investor_router)
api_router.include_router(loan_router)
api_router.include_router(loan_schedule_router)
api_router.include_router(loan_servicing_router)
api_router.include_router(underwriting_router)
api_router.include_router(reports_router)
api_router.include_router(payment_router)
api_router.include_router(ledger_router)
api_router.include_router(collection_router)
api_router.include_router(dashboard_router)
api_router.include_router(ai_router)
api_router.include_router(document_router)
# Later milestones register their module routers here.
