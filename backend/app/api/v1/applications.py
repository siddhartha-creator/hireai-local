from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_application_service, require_roles
from app.models.user import User
from app.modules.applications.service import ApplicationService
from app.schemas.jobs import ApplicationCreate, ApplicationRead, ApplicationStatusUpdate


router = APIRouter()


@router.get("/status")
async def applications_status() -> dict:
    return {"module": "applications", "status": "ready"}


@router.post("", response_model=ApplicationRead, status_code=201)
async def apply_to_job(
    payload: ApplicationCreate,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.apply_to_job(current_user, payload)


@router.get("", response_model=list[ApplicationRead])
async def list_all_applications(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.list_all_applications(current_user)


@router.get("/me", response_model=list[ApplicationRead])
async def list_my_applications(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.list_my_applications(current_user)


@router.get("/job/{job_id}", response_model=list[ApplicationRead])
async def list_applications_for_job(
    job_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.list_applications_for_job(current_user, job_id)


@router.get("/{application_id}", response_model=ApplicationRead)
async def read_application(
    application_id: UUID,
    current_user: CurrentUserDependency,
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.get_application(current_user, application_id)


@router.put("/{application_id}/status", response_model=ApplicationRead)
async def update_application_status(
    application_id: UUID,
    payload: ApplicationStatusUpdate,
    current_user: Annotated[User, Depends(require_roles(["admin", "recruiter"]))],
    application_service: Annotated[ApplicationService, Depends(get_application_service)],
):
    return application_service.update_application_status(current_user, application_id, payload)
