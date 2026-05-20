from fastapi.testclient import TestClient


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


def seed_application_flow(client: TestClient) -> tuple[str, str, dict]:
    register_user(client, email="recruiter@example.com", role="recruiter")
    recruiter_token = login_user(client, email="recruiter@example.com")
    job_response = client.post(
        "/api/v1/jobs",
        headers=headers(recruiter_token),
        json={
            "title": "Backend Engineer",
            "description": "Build FastAPI systems.",
            "skills_json": ["python", "fastapi"],
            "seniority": "mid",
            "location": "London",
            "status": "open",
        },
    )
    assert job_response.status_code == 201
    job = job_response.json()

    register_user(client, email="candidate@example.com", role="candidate")
    candidate_token = login_user(client, email="candidate@example.com")
    profile_response = client.put(
        "/api/v1/candidates/me",
        headers=headers(candidate_token),
        json={
            "headline": "Backend Engineer",
            "summary": "Python FastAPI developer.",
            "location": "London",
            "skills_json": ["python", "fastapi"],
            "experience_years": 5,
        },
    )
    assert profile_response.status_code == 200

    application_response = client.post(
        "/api/v1/applications",
        headers=headers(candidate_token),
        json={"job_id": job["id"], "cover_letter": "Interested."},
    )
    assert application_response.status_code == 201
    application = application_response.json()

    score_response = client.post(
        f"/api/v1/scoring/applications/{application['id']}/score",
        headers=headers(candidate_token),
    )
    assert score_response.status_code == 200

    session_response = client.post(
        "/api/v1/interviews/sessions",
        headers=headers(candidate_token),
        json={"application_id": application["id"]},
    )
    assert session_response.status_code == 201
    question_id = session_response.json()["questions"][0]["id"]
    answer_response = client.post(
        f"/api/v1/interviews/questions/{question_id}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I used FastAPI with SQLAlchemy, Docker, PostgreSQL, and pytest."},
    )
    assert answer_response.status_code == 200
    complete_response = client.post(
        f"/api/v1/interviews/sessions/{session_response.json()['id']}/complete",
        headers=headers(candidate_token),
    )
    assert complete_response.status_code == 200

    return recruiter_token, candidate_token, application


def test_recruiter_dashboard_aggregates_owned_jobs(client: TestClient) -> None:
    recruiter_token, _, _ = seed_application_flow(client)

    response = client.get("/api/v1/analytics/recruiter/dashboard", headers=headers(recruiter_token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 1
    assert data["open_jobs"] == 1
    assert data["total_applications"] == 1
    assert data["average_match_score"] is not None
    assert data["average_interview_score"] is not None
    assert data["top_skills_requested"][0]["skill"] in {"python", "fastapi"}


def test_candidate_dashboard_aggregates_own_activity(client: TestClient) -> None:
    _, candidate_token, _ = seed_application_flow(client)

    response = client.get("/api/v1/analytics/candidate/dashboard", headers=headers(candidate_token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 1
    assert data["completed_interviews"] == 1
    assert data["average_match_score"] is not None
    assert data["application_status_breakdown"][0]["status"] == "submitted"


def test_candidate_cannot_view_recruiter_dashboard(client: TestClient) -> None:
    _, candidate_token, _ = seed_application_flow(client)

    response = client.get("/api/v1/analytics/recruiter/dashboard", headers=headers(candidate_token))

    assert response.status_code == 403


def test_admin_platform_analytics(client: TestClient) -> None:
    seed_application_flow(client)
    register_user(client, email="admin@example.com", role="admin")
    admin_token = login_user(client, email="admin@example.com")

    response = client.get("/api/v1/analytics/platform", headers=headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 3
    assert data["total_candidates"] == 1
    assert data["total_recruiters"] == 1
    assert data["total_applications"] == 1
    assert data["total_interviews"] == 1
