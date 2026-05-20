from types import SimpleNamespace

from app.modules.ai_services.interviews.rule_based_answer_scorer import RuleBasedInterviewAnswerScorer
from app.modules.ai_services.interviews.rule_based_question_generator import RuleBasedInterviewQuestionGenerator


def test_rule_based_question_generator_creates_expected_question_mix() -> None:
    candidate = SimpleNamespace(skills_json=["python"], headline="Backend Engineer")
    resume = SimpleNamespace(extracted_skills_json=["docker"])
    job = SimpleNamespace(title="Backend Engineer", description="Build APIs", skills_json=["python", "fastapi", "postgresql"])
    match_score = SimpleNamespace(matched_skills_json=["python"])

    questions = RuleBasedInterviewQuestionGenerator().generate_questions(candidate, resume, job, match_score)
    question_types = {question.question_type for question in questions}

    assert len(questions) == 6
    assert "technical" in question_types
    assert "behavioral" in question_types
    assert "resume_based" in question_types
    assert "role_specific" in question_types
    assert all("keywords" in question.expected_signals_json for question in questions)


def test_rule_based_answer_scorer_scores_good_answer() -> None:
    question = SimpleNamespace(
        expected_signals_json={"keywords": ["fastapi", "project"]},
        skill_tag="fastapi",
    )
    job = SimpleNamespace(title="Backend Engineer")
    candidate = SimpleNamespace(headline="Backend Engineer")

    result = RuleBasedInterviewAnswerScorer().score_answer(
        question,
        "I built a FastAPI project, designed the API, solved performance issues, and improved the result.",
        job,
        candidate,
    )

    assert result.score > 5
    assert result.feedback_json["strengths"]


def test_rule_based_answer_scorer_penalizes_short_answer() -> None:
    question = SimpleNamespace(expected_signals_json={"keywords": ["fastapi"]}, skill_tag="fastapi")
    job = SimpleNamespace(title="Backend Engineer")
    candidate = SimpleNamespace(headline="Backend Engineer")

    result = RuleBasedInterviewAnswerScorer().score_answer(question, "yes", job, candidate)

    assert result.score == 0
    assert result.feedback_json["improvements"]
