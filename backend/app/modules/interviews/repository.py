from app.repositories.base import BaseRepository
from app.models.interview import CandidateAnswer, InterviewQuestion, InterviewSession


class InterviewRepository(BaseRepository[InterviewSession]):
    """Interview persistence."""

    def create_session(self, *, application_id, candidate_id, job_id) -> InterviewSession:
        session = InterviewSession(application_id=application_id, candidate_id=candidate_id, job_id=job_id)
        self.db.add(session)
        self.db.flush()
        self.db.refresh(session)
        return session

    def add_question(self, *, session_id, generated_question) -> InterviewQuestion:
        question = InterviewQuestion(
            session_id=session_id,
            question_text=generated_question.question_text,
            question_type=generated_question.question_type,
            skill_tag=generated_question.skill_tag,
            expected_signals_json=generated_question.expected_signals_json,
            order_index=generated_question.order_index,
        )
        self.db.add(question)
        self.db.flush()
        self.db.refresh(question)
        return question

    def get_session_by_id(self, session_id) -> InterviewSession | None:
        return self.db.get(InterviewSession, session_id)

    def get_question_by_id(self, question_id) -> InterviewQuestion | None:
        return self.db.get(InterviewQuestion, question_id)

    def get_answer_by_question_id(self, question_id) -> CandidateAnswer | None:
        return self.db.query(CandidateAnswer).filter(CandidateAnswer.question_id == question_id).first()

    def upsert_answer(self, *, question: InterviewQuestion, answer_text: str, score: float, feedback_json: dict) -> CandidateAnswer:
        answer = self.get_answer_by_question_id(question.id)
        if answer:
            answer.answer_text = answer_text
            answer.score = score
            answer.feedback_json = feedback_json
        else:
            answer = CandidateAnswer(
                question_id=question.id,
                answer_text=answer_text,
                score=score,
                feedback_json=feedback_json,
            )
            self.db.add(answer)
        self.db.flush()
        self.db.refresh(answer)
        return answer

    def list_by_candidate(self, candidate_id) -> list[InterviewSession]:
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.candidate_id == candidate_id)
            .order_by(InterviewSession.created_at.desc())
            .all()
        )

    def list_by_application(self, application_id) -> list[InterviewSession]:
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.application_id == application_id)
            .order_by(InterviewSession.created_at.desc())
            .all()
        )

    def list_all(self) -> list[InterviewSession]:
        return self.db.query(InterviewSession).order_by(InterviewSession.created_at.desc()).all()
