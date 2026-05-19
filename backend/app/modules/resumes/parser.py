from io import BytesIO

from docx import Document
from pypdf import PdfReader

from app.schemas.resumes import ParsedResumeData


class ResumeParserService:
    def extract_text(self, *, content: bytes, file_type: str) -> str:
        if file_type == "pdf":
            return self._extract_pdf_text(content)
        if file_type == "docx":
            return self._extract_docx_text(content)
        return ""

    def build_parsed_data(self, *, text: str, skills: list[str]) -> ParsedResumeData:
        return ParsedResumeData(
            skills=skills,
            education=[],
            experience=[],
            summary=text[:500],
            parser_version="rule_based_v1",
        )

    @staticmethod
    def _extract_pdf_text(content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        page_text = []
        for page in reader.pages:
            page_text.append(page.extract_text() or "")
        return "\n".join(page_text).strip()

    @staticmethod
    def _extract_docx_text(content: bytes) -> str:
        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
