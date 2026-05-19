from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    applications,
    auth,
    candidates,
    health,
    interviews,
    jobs,
    recruiters,
    resumes,
    scoring,
    users,
)


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(recruiters.router, prefix="/recruiters", tags=["recruiters"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
