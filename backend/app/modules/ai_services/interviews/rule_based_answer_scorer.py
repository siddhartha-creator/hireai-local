import re

from app.modules.ai_services.interviews.interface import AnswerScoreResult, InterviewAnswerScorerInterface


class RuleBasedInterviewAnswerScorer(InterviewAnswerScorerInterface):
    def score_answer(self, question, answer: str, job, candidate_profile) -> AnswerScoreResult:
        normalized = answer.strip().lower()
        words = re.findall(r"[a-z0-9.+#-]+", normalized)
        if len(words) < 3:
            return AnswerScoreResult(
                score=0.0,
                feedback_json={
                    "summary": "Answer is too short to evaluate.",
                    "strengths": [],
                    "improvements": ["Provide a fuller answer with examples."],
                    "score_reason": "Very short or empty answer.",
                },
            )

        expected = question.expected_signals_json or {}
        keywords = [str(keyword).lower() for keyword in expected.get("keywords", [])]
        keyword_hits = [keyword for keyword in keywords if keyword and keyword in normalized]
        score = 0.0

        score += min(len(words) / 40, 1.0) * 3.0
        score += min(len(keyword_hits) / max(len(keywords), 1), 1.0) * 3.0

        relevance_terms = [question.skill_tag, job.title, candidate_profile.headline]
        relevance_hits = [term for term in relevance_terms if term and str(term).lower() in normalized]
        score += min(len(relevance_hits) / 2, 1.0) * 2.0

        evidence_terms = ["project", "built", "implemented", "designed", "solved", "improved", "result"]
        evidence_hits = [term for term in evidence_terms if term in normalized]
        score += min(len(evidence_hits) / 2, 1.0) * 2.0

        final_score = round(min(score, 10.0), 2)
        strengths = []
        improvements = []
        if keyword_hits:
            strengths.append("Mentions expected signals.")
        else:
            improvements.append("Address the expected keywords more directly.")
        if evidence_hits:
            strengths.append("Includes practical evidence.")
        else:
            improvements.append("Add a concrete project or result.")

        return AnswerScoreResult(
            score=final_score,
            feedback_json={
                "summary": f"Answer scored {final_score}/10 using rule-based evaluation.",
                "strengths": strengths,
                "improvements": improvements,
                "score_reason": f"Length={len(words)} words, keyword_hits={len(keyword_hits)}, evidence_hits={len(evidence_hits)}.",
            },
        )
