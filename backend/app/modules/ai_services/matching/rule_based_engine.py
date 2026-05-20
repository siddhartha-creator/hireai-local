from app.modules.ai_services.matching.interface import MatchingEngineInterface, MatchScoreResult


class RuleBasedMatchingEngine(MatchingEngineInterface):
    SENIORITY_YEARS = {
        "internship": 0,
        "junior": 1,
        "mid": 3,
        "senior": 5,
        "lead": 7,
    }

    def score_application(self, candidate_profile, resume, job) -> MatchScoreResult:
        required_skills = self._normalize_list(job.skills_json)
        candidate_skills = set(self._normalize_list(candidate_profile.skills_json))
        if resume:
            candidate_skills.update(self._normalize_list(resume.extracted_skills_json))

        matched_skills = sorted(set(required_skills) & candidate_skills)
        missing_skills = sorted(set(required_skills) - candidate_skills)
        skill_score = self._score_skills(required_skills, matched_skills)

        experience_score = self._score_experience(candidate_profile.experience_years, job.seniority)
        education_score = self._score_education(resume)
        location_score = self._score_location(candidate_profile.location, job.location)

        overall_score = round(skill_score + experience_score + education_score + location_score, 2)
        recommendation = self._recommendation(overall_score)
        explanation = {
            "summary": f"Candidate is a {recommendation.replace('_', ' ')} with score {overall_score}/100.",
            "skill_reason": self._skill_reason(required_skills, matched_skills, missing_skills),
            "experience_reason": self._experience_reason(candidate_profile.experience_years, job.seniority, experience_score),
            "education_reason": "Education evidence found in parsed resume." if education_score else "No education evidence found in parsed resume.",
            "location_reason": self._location_reason(candidate_profile.location, job.location, location_score),
            "recommendation": recommendation,
        }

        return MatchScoreResult(
            overall_score=overall_score,
            skill_score=round(skill_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            location_score=round(location_score, 2),
            explanation_json=explanation,
            matched_skills_json=matched_skills,
            missing_skills_json=missing_skills,
        )

    def _score_skills(self, required_skills: list[str], matched_skills: list[str]) -> float:
        if not required_skills:
            return 25.0
        return len(matched_skills) / len(set(required_skills)) * 50

    def _score_experience(self, candidate_years: int | None, seniority: str | None) -> float:
        required_years = self.SENIORITY_YEARS.get((seniority or "").lower())
        if required_years is None:
            return 10.0
        candidate_years = candidate_years or 0
        if required_years == 0:
            return 25.0
        return min(candidate_years / required_years, 1.0) * 25

    def _score_education(self, resume) -> float:
        if not resume or not resume.parsed_data_json:
            return 0.0
        education = resume.parsed_data_json.get("education") or []
        return 10.0 if len(education) > 0 else 0.0

    def _score_location(self, candidate_location: str | None, job_location: str | None) -> float:
        if not candidate_location or not job_location:
            return 5.0
        candidate = candidate_location.strip().lower()
        job = job_location.strip().lower()
        if candidate == job or (candidate == "remote" and job == "remote"):
            return 15.0
        return 0.0

    def _skill_reason(self, required_skills: list[str], matched_skills: list[str], missing_skills: list[str]) -> str:
        if not required_skills:
            return "Job has no required skills, so neutral skill credit was applied."
        return f"Matched {len(matched_skills)} of {len(set(required_skills))} required skills. Missing: {', '.join(missing_skills) or 'none'}."

    def _experience_reason(self, candidate_years: int | None, seniority: str | None, score: float) -> str:
        required_years = self.SENIORITY_YEARS.get((seniority or "").lower())
        if required_years is None:
            return "Seniority requirement is missing or unknown, so neutral experience credit was applied."
        return f"Candidate has {candidate_years or 0} years; {seniority} expects about {required_years} years. Experience score: {round(score, 2)}/25."

    def _location_reason(self, candidate_location: str | None, job_location: str | None, score: float) -> str:
        if score == 15.0:
            return "Candidate location matches job location."
        if score == 5.0:
            return "Candidate or job location is missing, so neutral location credit was applied."
        return "Candidate location does not match job location."

    def _recommendation(self, overall_score: float) -> str:
        if overall_score >= 80:
            return "strong_match"
        if overall_score >= 50:
            return "moderate_match"
        return "weak_match"

    def _normalize_list(self, value) -> list[str]:
        if not value:
            return []
        if isinstance(value, dict):
            value = value.get("skills", [])
        return sorted({str(item).strip().lower() for item in value if str(item).strip()})
