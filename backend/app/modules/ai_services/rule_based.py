from app.modules.ai_services.interfaces import (
    InterviewQuestionGenerator,
    InterviewQuestionResult,
    MatchScoreResult,
    MatchingEngine,
    ParsedResume,
    ResumeParser,
)


class RuleBasedResumeParser(ResumeParser):
    def parse(self, text: str) -> ParsedResume:
        tokens = {token.strip(".,:;()").lower() for token in text.split()}
        known_skills = ["python", "fastapi", "sql", "react", "typescript", "docker"]
        skills = [skill for skill in known_skills if skill in tokens]
        return ParsedResume(extracted_text=text, skills=skills, experience_years=None, education=[])


class RuleBasedMatchingEngine(MatchingEngine):
    def score(self, candidate_profile: dict, resume_data: dict, job_data: dict) -> MatchScoreResult:
        candidate_skills = set(resume_data.get("skills", [])) | set(candidate_profile.get("skills", []))
        job_skills = set(job_data.get("skills", []))
        score = 0.0 if not job_skills else round(len(candidate_skills & job_skills) / len(job_skills) * 100, 2)
        return MatchScoreResult(score=score, explanation={"strategy": "skill_overlap", "matched": list(candidate_skills & job_skills)})


class RuleBasedInterviewQuestionGenerator(InterviewQuestionGenerator):
    def generate(self, candidate_profile: dict, resume_data: dict, job_data: dict) -> list[InterviewQuestionResult]:
        title = job_data.get("title", "this role")
        skills = job_data.get("skills", [])[:3]
        questions = [
            InterviewQuestionResult(
                question_text=f"Tell me about a project that prepared you for {title}.",
                question_type="experience",
                expected_signals=["relevance", "ownership", "impact"],
            )
        ]
        for skill in skills:
            questions.append(
                InterviewQuestionResult(
                    question_text=f"How have you applied {skill} in a practical project?",
                    question_type="technical",
                    expected_signals=["specificity", "depth", "tradeoffs"],
                )
            )
        return questions
