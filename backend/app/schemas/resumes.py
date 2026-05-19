from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ParsedResumeData(BaseModel):
    skills: list[str] = []
    education: list = []
    experience: list = []
    summary: str = ""
    parser_version: str = "rule_based_v1"


class ResumeListItem(BaseModel):
    id: UUID
    candidate_id: UUID
    file_name: str
    original_file_name: str
    file_type: str
    file_size: int
    extracted_skills_json: list | None
    is_primary: bool
    uploaded_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeRead(ResumeListItem):
    parsed_data_json: dict | None


class ResumeUploadResponse(BaseModel):
    resume: ResumeRead
    parsed_data: ParsedResumeData
