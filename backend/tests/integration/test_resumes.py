from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.modules.resumes.skills import SkillExtractionService


def register_user(client: TestClient, *, email: str, role: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": f"{role.title()} User",
            "password": "Password123!",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, *, email: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    assert response.status_code == 200
    return response.json()["access_token"]


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_candidate(client: TestClient, *, email: str = "candidate@example.com") -> str:
    register_user(client, email=email, role="candidate")
    return login_user(client, email=email)


def create_recruiter_job(client: TestClient, *, email: str = "recruiter@example.com") -> tuple[str, dict]:
    register_user(client, email=email, role="recruiter")
    token = login_user(client, email=email)
    response = client.post(
        "/api/v1/jobs",
        headers=headers(token),
        json={
            "title": "Backend Engineer",
            "description": "Build and maintain production FastAPI services.",
            "skills_json": ["python", "fastapi"],
            "status": "open",
        },
    )
    assert response.status_code == 201
    return token, response.json()


def make_pdf_bytes() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(output)
    return output.getvalue()


def make_docx_bytes(text: str = "Python FastAPI PostgreSQL Docker") -> bytes:
    output = BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(output)
    return output.getvalue()


def upload_resume(client: TestClient, token: str, *, filename: str = "resume.pdf", content: bytes | None = None):
    content = content if content is not None else make_pdf_bytes()
    return client.post(
        "/api/v1/resumes/upload",
        headers=headers(token),
        files={"file": (filename, content)},
    )


def test_candidate_can_upload_pdf_resume(client: TestClient) -> None:
    token = create_candidate(client)

    response = upload_resume(client, token)

    assert response.status_code == 201
    data = response.json()["resume"]
    assert data["file_type"] == "pdf"
    assert data["is_primary"] is True
    assert "file_path" not in data


def test_candidate_can_upload_docx_resume(client: TestClient) -> None:
    token = create_candidate(client)

    response = upload_resume(client, token, filename="resume.docx", content=make_docx_bytes())

    assert response.status_code == 201
    data = response.json()
    assert data["resume"]["file_type"] == "docx"
    assert "python" in data["parsed_data"]["skills"]
    assert "fastapi" in data["parsed_data"]["skills"]


def test_non_candidate_cannot_upload_resume(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = upload_resume(client, token)

    assert response.status_code == 403


def test_invalid_file_type_rejected(client: TestClient) -> None:
    token = create_candidate(client)

    response = upload_resume(client, token, filename="resume.txt", content=b"python")

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "invalid_file_type"


def test_file_larger_than_limit_rejected(client: TestClient) -> None:
    token = create_candidate(client)

    response = upload_resume(client, token, filename="resume.pdf", content=b"x" * (5 * 1024 * 1024 + 1))

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "file_too_large"


def test_first_uploaded_resume_becomes_primary(client: TestClient) -> None:
    token = create_candidate(client)

    response = upload_resume(client, token)

    assert response.status_code == 201
    assert response.json()["resume"]["is_primary"] is True


def test_marking_second_resume_primary_unsets_first(client: TestClient) -> None:
    token = create_candidate(client)
    first = upload_resume(client, token, filename="first.pdf").json()["resume"]
    second = upload_resume(client, token, filename="second.docx", content=make_docx_bytes()).json()["resume"]

    mark_response = client.put(f"/api/v1/resumes/{second['id']}/primary", headers=headers(token))
    list_response = client.get("/api/v1/resumes/me", headers=headers(token))

    assert mark_response.status_code == 200
    resumes = {resume["id"]: resume for resume in list_response.json()}
    assert resumes[first["id"]]["is_primary"] is False
    assert resumes[second["id"]]["is_primary"] is True


def test_candidate_can_list_own_resumes(client: TestClient) -> None:
    token = create_candidate(client)
    upload_resume(client, token)

    response = client.get("/api/v1/resumes/me", headers=headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_candidate_cannot_access_another_candidates_resume(client: TestClient) -> None:
    owner_token = create_candidate(client, email="owner@example.com")
    other_token = create_candidate(client, email="other@example.com")
    resume = upload_resume(client, owner_token).json()["resume"]

    response = client.get(f"/api/v1/resumes/{resume['id']}", headers=headers(other_token))

    assert response.status_code == 403


def test_recruiter_can_access_resume_metadata_for_candidate_who_applied(client: TestClient) -> None:
    recruiter_token, job = create_recruiter_job(client)
    candidate_token = create_candidate(client)
    resume = upload_resume(client, candidate_token).json()["resume"]
    client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job["id"]})

    response = client.get(f"/api/v1/resumes/{resume['id']}", headers=headers(recruiter_token))

    assert response.status_code == 200
    assert response.json()["id"] == resume["id"]
    assert "file_path" not in response.json()


def test_recruiter_cannot_access_unrelated_candidate_resume(client: TestClient) -> None:
    recruiter_token, _ = create_recruiter_job(client)
    candidate_token = create_candidate(client)
    resume = upload_resume(client, candidate_token).json()["resume"]

    response = client.get(f"/api/v1/resumes/{resume['id']}", headers=headers(recruiter_token))

    assert response.status_code == 403


def test_delete_removes_resume_record(client: TestClient) -> None:
    token = create_candidate(client)
    resume = upload_resume(client, token).json()["resume"]

    delete_response = client.delete(f"/api/v1/resumes/{resume['id']}", headers=headers(token))
    read_response = client.get(f"/api/v1/resumes/{resume['id']}", headers=headers(token))

    assert delete_response.status_code == 204
    assert read_response.status_code == 404


def test_skill_extraction_finds_expected_skills() -> None:
    skills = SkillExtractionService().extract(
        "Built Python FastAPI services with PostgreSQL, Docker, React, Next.js, and machine learning."
    )

    assert "python" in skills
    assert "fastapi" in skills
    assert "postgresql" in skills
    assert "docker" in skills
    assert "react" in skills
    assert "next.js" in skills
    assert "machine learning" in skills
