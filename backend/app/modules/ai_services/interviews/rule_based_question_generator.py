from app.modules.ai_services.interviews.interface import GeneratedQuestion, InterviewQuestionGeneratorInterface


class RuleBasedInterviewQuestionGenerator(InterviewQuestionGeneratorInterface):
    def generate_questions(self, candidate_profile, resume, job, match_score) -> list[GeneratedQuestion]:
        questions: list[GeneratedQuestion] = []
        job_skills = self._normalize_list(job.skills_json)
        candidate_skills = self._normalize_list(candidate_profile.skills_json)
        resume_skills = self._normalize_list(resume.extracted_skills_json if resume else [])
        matched_skills = self._normalize_list(match_score.matched_skills_json if match_score else [])
        technical_skills = (job_skills + matched_skills + candidate_skills)[:3]

        while len(technical_skills) < 3:
            technical_skills.append("backend engineering")

        for skill in technical_skills[:3]:
            questions.append(
                self._question(
                    f"How have you used {skill.title()} in a real project?",
                    "technical",
                    skill,
                    ["specific examples", "technical depth", skill],
                    len(questions),
                )
            )

        questions.append(
            self._question(
                "Tell me about a time you solved a difficult technical problem.",
                "behavioral",
                None,
                ["problem", "action", "result", "reflection"],
                len(questions),
            )
        )

        resume_skill = (resume_skills or candidate_skills or job_skills or ["your listed skills"])[0]
        questions.append(
            self._question(
                f"Your resume mentions {resume_skill.title()}. Can you explain how you used it?",
                "resume_based",
                resume_skill,
                ["resume evidence", "ownership", resume_skill],
                len(questions),
            )
        )

        questions.append(
            self._question(
                f"Why are you a strong fit for the {job.title} role?",
                "role_specific",
                job.title,
                ["role fit", "job understanding", "impact"],
                len(questions),
            )
        )

        return questions

    def _question(
        self,
        text: str,
        question_type: str,
        skill_tag: str | None,
        keywords: list[str],
        order_index: int,
    ) -> GeneratedQuestion:
        return GeneratedQuestion(
            question_text=text,
            question_type=question_type,
            skill_tag=skill_tag,
            expected_signals_json={
                "keywords": keywords,
                "good_answer_traits": ["specific", "structured", "evidence-backed"],
            },
            order_index=order_index,
        )

    @staticmethod
    def _normalize_list(value) -> list[str]:
        if not value:
            return []
        if isinstance(value, dict):
            value = value.get("skills", [])
        return [str(item).strip().lower() for item in value if str(item).strip()]
