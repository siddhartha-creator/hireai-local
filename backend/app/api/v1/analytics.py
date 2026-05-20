from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_analytics_service, require_roles
from app.modules.analytics.service import AnalyticsService
from app.schemas.analytics import CandidateDashboardResponse, PlatformAnalyticsResponse, RecruiterDashboardResponse


router = APIRouter()


@router.get("/status")
async def analytics_status() -> dict:
    return {"module": "analytics", "status": "ready"}


@router.get(
    "/recruiter/dashboard",
    response_model=RecruiterDashboardResponse,
    dependencies=[Depends(require_roles(["recruiter"]))],
)
async def recruiter_dashboard(
    current_user: CurrentUserDependency,
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> RecruiterDashboardResponse:
    return analytics_service.recruiter_dashboard(current_user)


@router.get(
    "/candidate/dashboard",
    response_model=CandidateDashboardResponse,
    dependencies=[Depends(require_roles(["candidate"]))],
)
async def candidate_dashboard(
    current_user: CurrentUserDependency,
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> CandidateDashboardResponse:
    return analytics_service.candidate_dashboard(current_user)


@router.get(
    "/platform",
    response_model=PlatformAnalyticsResponse,
    dependencies=[Depends(require_roles(["admin"]))],
)
async def platform_analytics(
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> PlatformAnalyticsResponse:
    return analytics_service.platform_analytics()
