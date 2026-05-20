from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_scoring_service, require_roles
from app.models.user import User
from app.modules.scoring.service import ScoringService
from app.schemas.scoring import MatchScoreListItem, MatchScoreRead, ScoreApplicationResponse


router = APIRouter()


@router.get("/status")
async def scoring_status() -> dict:
    return {"module": "scoring", "status": "ready"}


@router.post("/applications/{application_id}/score", response_model=ScoreApplicationResponse)
async def score_application(
    application_id: UUID,
    current_user: CurrentUserDependency,
    scoring_service: Annotated[ScoringService, Depends(get_scoring_service)],
):
    return scoring_service.score_application(current_user, application_id)


@router.get("/applications/{application_id}", response_model=MatchScoreRead)
async def read_application_score(
    application_id: UUID,
    current_user: CurrentUserDependency,
    scoring_service: Annotated[ScoringService, Depends(get_scoring_service)],
):
    return scoring_service.get_score_for_application(current_user, application_id)


@router.get("/jobs/{job_id}", response_model=list[MatchScoreListItem])
async def list_job_scores(
    job_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    scoring_service: Annotated[ScoringService, Depends(get_scoring_service)],
):
    return scoring_service.list_scores_for_job(current_user, job_id)


@router.get("/me", response_model=list[MatchScoreListItem])
async def list_my_scores(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    scoring_service: Annotated[ScoringService, Depends(get_scoring_service)],
):
    return scoring_service.list_my_scores(current_user)


@router.get("", response_model=list[MatchScoreListItem])
async def list_all_scores(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    scoring_service: Annotated[ScoringService, Depends(get_scoring_service)],
):
    return scoring_service.list_all_scores(current_user)
