import re


class SkillExtractionService:
    SKILL_KEYWORDS = [
        "python",
        "fastapi",
        "django",
        "flask",
        "javascript",
        "typescript",
        "react",
        "next.js",
        "node.js",
        "express",
        "sql",
        "postgresql",
        "mongodb",
        "docker",
        "git",
        "aws",
        "machine learning",
        "nlp",
        "data analysis",
        "html",
        "css",
        "tailwind",
    ]

    def extract(self, text: str) -> list[str]:
        normalized = text.lower()
        found = []
        for keyword in self.SKILL_KEYWORDS:
            pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                found.append(keyword)
        return found
