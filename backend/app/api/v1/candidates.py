from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_candidate_service, require_roles
from app.models.user import User
from app.modules.candidates.service import CandidateService
from app.schemas.profiles import CandidateProfileRead, CandidateProfileUpdate


router = APIRouter()


@router.get("/status")
async def candidates_status(
    current_user: Annotated[User, Depends(require_roles(["admin", "candidate"]))],
) -> dict:
    return {"module": "candidates", "status": "ready"}


@router.get("/me", response_model=CandidateProfileRead)
async def read_candidate_profile_me(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    candidate_service: Annotated[CandidateService, Depends(get_candidate_service)],
):
    return candidate_service.get_own_profile(current_user)


@router.put("/me", response_model=CandidateProfileRead)
async def update_candidate_profile_me(
    payload: CandidateProfileUpdate,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    candidate_service: Annotated[CandidateService, Depends(get_candidate_service)],
):
    return candidate_service.update_own_profile(current_user, payload)


@router.get("/{candidate_id}", response_model=CandidateProfileRead)
async def read_candidate_profile_by_id(
    candidate_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    candidate_service: Annotated[CandidateService, Depends(get_candidate_service)],
):
    return candidate_service.get_profile_by_id(candidate_id)
