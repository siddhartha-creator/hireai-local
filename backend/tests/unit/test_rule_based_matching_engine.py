from types import SimpleNamespace

from app.modules.ai_services.matching.rule_based_engine import RuleBasedMatchingEngine


def test_rule_based_engine_strong_match() -> None:
    candidate = SimpleNamespace(skills_json=["python", "fastapi"], experience_years=5, location="London")
    resume = SimpleNamespace(
        extracted_skills_json=["postgresql", "docker"],
        parsed_data_json={"education": ["BSc Computer Science"]},
    )
    job = SimpleNamespace(skills_json=["python", "fastapi", "postgresql"], seniority="mid", location="London")

    result = RuleBasedMatchingEngine().score_application(candidate, resume, job)

    assert result.overall_score >= 80
    assert result.explanation_json["recommendation"] == "strong_match"
    assert result.matched_skills_json == ["fastapi", "postgresql", "python"]
    assert result.missing_skills_json == []


def test_rule_based_engine_weak_match() -> None:
    candidate = SimpleNamespace(skills_json=["html"], experience_years=0, location="Manchester")
    resume = SimpleNamespace(extracted_skills_json=[], parsed_data_json={"education": []})
    job = SimpleNamespace(skills_json=["python", "fastapi"], seniority="senior", location="London")

    result = RuleBasedMatchingEngine().score_application(candidate, resume, job)

    assert result.overall_score < 50
    assert result.explanation_json["recommendation"] == "weak_match"
    assert result.matched_skills_json == []
    assert result.missing_skills_json == ["fastapi", "python"]


def test_rule_based_engine_without_resume_uses_profile_only() -> None:
    candidate = SimpleNamespace(skills_json=["python"], experience_years=1, location="Remote")
    job = SimpleNamespace(skills_json=["python", "docker"], seniority="junior", location="Remote")

    result = RuleBasedMatchingEngine().score_application(candidate, None, job)

    assert result.skill_score == 25
    assert result.education_score == 0
    assert result.location_score == 15
