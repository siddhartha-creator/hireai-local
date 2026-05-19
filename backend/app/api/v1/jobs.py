from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_job_service, require_roles
from app.models.user import User
from app.modules.jobs.service import JobService
from app.schemas.jobs import JobCreate, JobListItem, JobRead, JobUpdate


router = APIRouter()


@router.get("/status")
async def jobs_status() -> dict:
    return {"module": "jobs", "status": "ready"}


@router.post("", response_model=JobRead, status_code=201)
async def create_job(
    payload: JobCreate,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    job_service: Annotated[JobService, Depends(get_job_service)],
):
    return job_service.create_job(current_user, payload)


@router.get("", response_model=list[JobListItem])
async def list_jobs(
    current_user: CurrentUserDependency,
    job_service: Annotated[JobService, Depends(get_job_service)],
):
    return job_service.list_jobs(current_user)


@router.get("/{job_id}", response_model=JobRead)
async def read_job(
    job_id: UUID,
    current_user: CurrentUserDependency,
    job_service: Annotated[JobService, Depends(get_job_service)],
):
    return job_service.get_job(current_user, job_id)


@router.put("/{job_id}", response_model=JobRead)
async def update_job(
    job_id: UUID,
    payload: JobUpdate,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    job_service: Annotated[JobService, Depends(get_job_service)],
):
    return job_service.update_job(current_user, job_id, payload)


@router.delete("/{job_id}", response_model=JobRead)
async def delete_job(
    job_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    job_service: Annotated[JobService, Depends(get_job_service)],
):
    return job_service.archive_job(current_user, job_id)
