from app.repositories.base import BaseRepository
from app.models.scoring import MatchScore


class ScoringRepository(BaseRepository[MatchScore]):
    """Match score persistence."""

    def get_by_application_id(self, application_id) -> MatchScore | None:
        return self.db.query(MatchScore).filter(MatchScore.application_id == application_id).first()

    def get_by_id(self, score_id) -> MatchScore | None:
        return self.db.get(MatchScore, score_id)

    def list_by_candidate(self, candidate_id) -> list[MatchScore]:
        return (
            self.db.query(MatchScore)
            .filter(MatchScore.candidate_id == candidate_id)
            .order_by(MatchScore.created_at.desc())
            .all()
        )

    def list_by_job(self, job_id) -> list[MatchScore]:
        return (
            self.db.query(MatchScore)
            .filter(MatchScore.job_id == job_id)
            .order_by(MatchScore.created_at.desc())
            .all()
        )

    def list_all(self) -> list[MatchScore]:
        return self.db.query(MatchScore).order_by(MatchScore.created_at.desc()).all()

    def upsert_for_application(self, *, application, result) -> MatchScore:
        score = self.get_by_application_id(application.id)
        if not score:
            score = MatchScore(
                application_id=application.id,
                candidate_id=application.candidate_id,
                job_id=application.job_id,
                overall_score=result.overall_score,
                skill_score=result.skill_score,
                experience_score=result.experience_score,
                education_score=result.education_score,
                location_score=result.location_score,
                explanation_json=result.explanation_json,
                matched_skills_json=result.matched_skills_json,
                missing_skills_json=result.missing_skills_json,
                scoring_version=result.scoring_version,
            )
            self.db.add(score)
        else:
            score.overall_score = result.overall_score
            score.skill_score = result.skill_score
            score.experience_score = result.experience_score
            score.education_score = result.education_score
            score.location_score = result.location_score
            score.explanation_json = result.explanation_json
            score.matched_skills_json = result.matched_skills_json
            score.missing_skills_json = result.missing_skills_json
            score.scoring_version = result.scoring_version
        self.db.flush()
        self.db.refresh(score)
        return score
