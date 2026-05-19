from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedResume:
    extracted_text: str
    skills: list[str]
    experience_years: int | None
    education: list[str]


@dataclass(frozen=True)
class MatchScoreResult:
    score: float
    explanation: dict


@dataclass(frozen=True)
class InterviewQuestionResult:
    question_text: str
    question_type: str
    expected_signals: list[str]


class ResumeParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParsedResume:
        raise NotImplementedError


class MatchingEngine(ABC):
    @abstractmethod
    def score(self, candidate_profile: dict, resume_data: dict, job_data: dict) -> MatchScoreResult:
        raise NotImplementedError


class InterviewQuestionGenerator(ABC):
    @abstractmethod
    def generate(self, candidate_profile: dict, resume_data: dict, job_data: dict) -> list[InterviewQuestionResult]:
        raise NotImplementedError
