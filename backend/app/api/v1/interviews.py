from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_interview_service, require_roles
from app.models.user import User
from app.modules.interviews.service import InterviewService
from app.schemas.interviews import (
    CandidateAnswerCreate,
    CandidateAnswerRead,
    InterviewSessionCreate,
    InterviewSessionRead,
    InterviewSessionSummary,
)


router = APIRouter()


@router.get("/status")
async def interviews_status() -> dict:
    return {"module": "interviews", "status": "ready"}


@router.post("/sessions", response_model=InterviewSessionRead, status_code=201)
async def start_interview_session(
    payload: InterviewSessionCreate,
    current_user: CurrentUserDependency,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.start_session(current_user, payload)


@router.get("/sessions/{session_id}", response_model=InterviewSessionRead)
async def read_interview_session(
    session_id: UUID,
    current_user: CurrentUserDependency,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.get_session(current_user, session_id)


@router.post("/sessions/{session_id}/complete", response_model=InterviewSessionRead)
async def complete_interview_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.complete_session(current_user, session_id)


@router.get("/me", response_model=list[InterviewSessionSummary])
async def list_my_interviews(
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.list_my_sessions(current_user)


@router.get("/applications/{application_id}", response_model=list[InterviewSessionSummary])
async def list_application_interviews(
    application_id: UUID,
    current_user: CurrentUserDependency,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.list_application_sessions(current_user, application_id)


@router.get("", response_model=list[InterviewSessionSummary])
async def list_all_interviews(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.list_all_sessions(current_user)


@router.post("/questions/{question_id}/answer", response_model=CandidateAnswerRead)
async def answer_interview_question(
    question_id: UUID,
    payload: CandidateAnswerCreate,
    current_user: Annotated[User, Depends(require_roles(["candidate"]))],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    return interview_service.answer_question(current_user, question_id, payload)
