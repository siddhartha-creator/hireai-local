from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_recruiter_service, require_roles
from app.models.user import User
from app.modules.recruiters.service import RecruiterService
from app.schemas.profiles import RecruiterProfileRead, RecruiterProfileUpdate


router = APIRouter()


@router.get("/status")
async def recruiters_status(
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
) -> dict:
    return {"module": "recruiters", "status": "ready"}


@router.get("/me", response_model=RecruiterProfileRead)
async def read_recruiter_profile_me(
    current_user: Annotated[User, Depends(require_roles(["recruiter"]))],
    recruiter_service: Annotated[RecruiterService, Depends(get_recruiter_service)],
):
    return recruiter_service.get_own_profile(current_user)


@router.put("/me", response_model=RecruiterProfileRead)
async def update_recruiter_profile_me(
    payload: RecruiterProfileUpdate,
    current_user: Annotated[User, Depends(require_roles(["recruiter"]))],
    recruiter_service: Annotated[RecruiterService, Depends(get_recruiter_service)],
):
    return recruiter_service.update_own_profile(current_user, payload)


@router.get("/{recruiter_id}", response_model=RecruiterProfileRead)
async def read_recruiter_profile_by_id(
    recruiter_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    recruiter_service: Annotated[RecruiterService, Depends(get_recruiter_service)],
):
    return recruiter_service.get_profile_by_id(recruiter_id)
