from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class MatchScoreResult:
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    explanation_json: dict
    matched_skills_json: list[str]
    missing_skills_json: list[str]
    scoring_version: str = "rule_based_v1"


class MatchingEngineInterface(ABC):
    @abstractmethod
    def score_application(self, candidate_profile, resume, job) -> MatchScoreResult:
        raise NotImplementedError
