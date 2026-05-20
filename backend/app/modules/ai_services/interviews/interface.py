from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedQuestion:
    question_text: str
    question_type: str
    skill_tag: str | None
    expected_signals_json: dict
    order_index: int


@dataclass(frozen=True)
class AnswerScoreResult:
    score: float
    feedback_json: dict


class InterviewQuestionGeneratorInterface(ABC):
    @abstractmethod
    def generate_questions(self, candidate_profile, resume, job, match_score) -> list[GeneratedQuestion]:
        raise NotImplementedError


class InterviewAnswerScorerInterface(ABC):
    @abstractmethod
    def score_answer(self, question, answer: str, job, candidate_profile) -> AnswerScoreResult:
        raise NotImplementedError
