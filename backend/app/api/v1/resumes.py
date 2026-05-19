from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from app.core.dependencies import CurrentUserDependency, get_resume_service, require_roles
from app.models.user import User
from app.modules.resumes.service import ResumeService
from app.schemas.resumes import ParsedResumeData, ResumeListItem, ResumeRead, ResumeUploadResponse


router = APIRouter()


@router.get("/status")
async def resumes_status() -> dict:
    return {"module": "resumes", "status": "ready"}


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
    file: UploadFile = File(...),
):
    return await resume_service.upload_resume(current_user, file)


@router.get("/me", response_model=list[ResumeListItem])
async def list_my_resumes(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
):
    return resume_service.list_my_resumes(current_user)


@router.get("/{resume_id}", response_model=ResumeRead)
async def read_resume(
    resume_id: UUID,
    current_user: CurrentUserDependency,
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
):
    return resume_service.get_resume(current_user, resume_id)


@router.get("/{resume_id}/parsed", response_model=ParsedResumeData)
async def read_parsed_resume(
    resume_id: UUID,
    current_user: CurrentUserDependency,
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
):
    return resume_service.get_parsed_resume(current_user, resume_id)


@router.put("/{resume_id}/primary", response_model=ResumeRead)
async def mark_resume_primary(
    resume_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
):
    return resume_service.mark_primary(current_user, resume_id)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
):
    resume_service.delete_resume(current_user, resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
