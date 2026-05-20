from uuid import UUID

from app.core.exceptions import ConflictError, PermissionDeniedError, ResourceNotFoundError
from app.core.time import utc_now
from app.models.application import Application
from app.models.interview import InterviewQuestion, InterviewSession
from app.models.job import Job
from app.models.user import User
from app.modules.ai_services.interviews.interface import (
    InterviewAnswerScorerInterface,
    InterviewQuestionGeneratorInterface,
)
from app.modules.applications.repository import ApplicationRepository
from app.modules.candidates.repository import CandidateRepository
from app.modules.interviews.repository import InterviewRepository
from app.modules.jobs.repository import JobRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.modules.resumes.repository import ResumeRepository
from app.modules.scoring.repository import ScoringRepository
from app.schemas.interviews import CandidateAnswerCreate, InterviewFeedback, InterviewSessionCreate
from app.services.base import BaseService


class InterviewService(BaseService):
    """Interview session orchestration."""

    def __init__(
        self,
        interview_repository: InterviewRepository,
        application_repository: ApplicationRepository,
        candidate_repository: CandidateRepository,
        recruiter_repository: RecruiterRepository,
        job_repository: JobRepository,
        resume_repository: ResumeRepository,
        scoring_repository: ScoringRepository,
        question_generator: InterviewQuestionGeneratorInterface,
        answer_scorer: InterviewAnswerScorerInterface,
    ) -> None:
        self.interview_repository = interview_repository
        self.application_repository = application_repository
        self.candidate_repository = candidate_repository
        self.recruiter_repository = recruiter_repository
        self.job_repository = job_repository
        self.resume_repository = resume_repository
        self.scoring_repository = scoring_repository
        self.question_generator = question_generator
        self.answer_scorer = answer_scorer

    def start_session(self, current_user: User, payload: InterviewSessionCreate) -> InterviewSession:
        application = self._get_existing_application(payload.application_id)
        self._assert_can_access_application(current_user, application)
        candidate = self.candidate_repository.get_by_id(application.candidate_id)
        job = self._get_existing_job(application.job_id)
        if not candidate:
            raise ResourceNotFoundError("Candidate profile not found", details=[{"code": "candidate_profile_not_found"}])
        resume = self.resume_repository.get_primary_by_candidate(candidate.id)
        match_score = self.scoring_repository.get_by_application_id(application.id)

        session = self.interview_repository.create_session(
            application_id=application.id,
            candidate_id=application.candidate_id,
            job_id=application.job_id,
        )
        generated_questions = self.question_generator.generate_questions(candidate, resume, job, match_score)
        for generated_question in generated_questions:
            self.interview_repository.add_question(session_id=session.id, generated_question=generated_question)
        self.interview_repository.db.commit()
        self.interview_repository.db.refresh(session)
        return session

    def get_session(self, current_user: User, session_id: UUID) -> InterviewSession:
        session = self._get_existing_session(session_id)
        self._assert_can_access_session(current_user, session)
        return session

    def list_my_sessions(self, current_user: User) -> list[InterviewSession]:
        candidate = self.candidate_repository.get_by_user_id(current_user.id)
        return self.interview_repository.list_by_candidate(candidate.id) if candidate else []

    def list_application_sessions(self, current_user: User, application_id: UUID) -> list[InterviewSession]:
        application = self._get_existing_application(application_id)
        self._assert_can_access_application(current_user, application)
        return self.interview_repository.list_by_application(application.id)

    def list_all_sessions(self, current_user: User) -> list[InterviewSession]:
        if not self._has_role(current_user, "admin"):
            raise PermissionDeniedError("Admin role is required", details=[{"code": "admin_required"}])
        return self.interview_repository.list_all()

    def answer_question(self, current_user: User, question_id: UUID, payload: CandidateAnswerCreate):
        question = self._get_existing_question(question_id)
        session = self._get_existing_session(question.session_id)
        self._assert_candidate_owns_session(current_user, session)
        if session.status in {"completed", "cancelled"}:
            raise ConflictError("Cannot answer questions after session is closed", details=[{"code": "session_closed"}])
        job = self._get_existing_job(session.job_id)
        candidate = self.candidate_repository.get_by_id(session.candidate_id)
        if not candidate:
            raise ResourceNotFoundError("Candidate profile not found", details=[{"code": "candidate_profile_not_found"}])
        result = self.answer_scorer.score_answer(question, payload.answer_text, job, candidate)
        answer = self.interview_repository.upsert_answer(
            question=question,
            answer_text=payload.answer_text,
            score=result.score,
            feedback_json=result.feedback_json,
        )
        self.interview_repository.db.commit()
        self.interview_repository.db.refresh(answer)
        return answer

    def complete_session(self, current_user: User, session_id: UUID) -> InterviewSession:
        session = self._get_existing_session(session_id)
        self._assert_candidate_owns_session(current_user, session)
        if session.status in {"completed", "cancelled"}:
            raise ConflictError("Interview session is already closed", details=[{"code": "session_closed"}])
        answered_questions = [question for question in session.questions if question.answer and question.answer.score is not None]
        if not answered_questions:
            raise ConflictError("At least one answered question is required", details=[{"code": "no_answers"}])
        average_answer_score = sum(question.answer.score for question in answered_questions) / len(answered_questions)
        overall_score = round(average_answer_score * 10, 2)
        session.overall_score = overall_score
        session.status = "completed"
        session.completed_at = utc_now()
        session.feedback_json = InterviewFeedback(
            summary=f"Interview completed with overall score {overall_score}/100.",
            strengths=["Completed answered questions with evaluable responses."],
            improvements=[] if overall_score >= 70 else ["Add more specific examples and expected keywords."],
        ).model_dump()
        self.interview_repository.db.commit()
        self.interview_repository.db.refresh(session)
        return session

    def _get_existing_application(self, application_id: UUID) -> Application:
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise ResourceNotFoundError("Application not found", details=[{"code": "application_not_found"}])
        return application

    def _get_existing_job(self, job_id: UUID) -> Job:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ResourceNotFoundError("Job not found", details=[{"code": "job_not_found"}])
        return job

    def _get_existing_session(self, session_id: UUID) -> InterviewSession:
        session = self.interview_repository.get_session_by_id(session_id)
        if not session:
            raise ResourceNotFoundError("Interview session not found", details=[{"code": "interview_session_not_found"}])
        return session

    def _get_existing_question(self, question_id: UUID) -> InterviewQuestion:
        question = self.interview_repository.get_question_by_id(question_id)
        if not question:
            raise ResourceNotFoundError("Interview question not found", details=[{"code": "interview_question_not_found"}])
        return question

    def _assert_can_access_session(self, current_user: User, session: InterviewSession) -> None:
        application = self._get_existing_application(session.application_id)
        self._assert_can_access_application(current_user, application)

    def _assert_can_access_application(self, current_user: User, application: Application) -> None:
        if self._has_role(current_user, "admin"):
            return
        if self._has_role(current_user, "candidate"):
            candidate = self.candidate_repository.get_by_user_id(current_user.id)
            if candidate and application.candidate_id == candidate.id:
                return
        if self._has_role(current_user, "recruiter"):
            job = self._get_existing_job(application.job_id)
            self._assert_recruiter_owns_job(current_user, job)
            return
        raise PermissionDeniedError("Insufficient interview permissions", details=[{"code": "interview_access_denied"}])

    def _assert_candidate_owns_session(self, current_user: User, session: InterviewSession) -> None:
        candidate = self.candidate_repository.get_by_user_id(current_user.id)
        if not candidate or session.candidate_id != candidate.id:
            raise PermissionDeniedError("Candidate does not own this interview", details=[{"code": "interview_owner_required"}])

    def _assert_recruiter_owns_job(self, current_user: User, job: Job) -> None:
        recruiter = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter or recruiter.id != job.recruiter_id:
            raise PermissionDeniedError("Recruiter does not own this job", details=[{"code": "job_owner_required"}])

    @staticmethod
    def _has_role(user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)
