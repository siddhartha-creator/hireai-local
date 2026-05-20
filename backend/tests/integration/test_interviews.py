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


def create_candidate(client: TestClient, *, email: str = "candidate@example.com") -> str:
    register_user(client, email=email, role="candidate")
    token = login_user(client, email=email)
    response = client.put(
        "/api/v1/candidates/me",
        headers=headers(token),
        json={
            "headline": "Backend Engineer",
            "summary": "Python FastAPI candidate.",
            "location": "London",
            "skills_json": ["python", "fastapi"],
            "experience_years": 3,
        },
    )
    assert response.status_code == 200
    return token


def create_recruiter_job(client: TestClient, *, email: str = "recruiter@example.com") -> tuple[str, dict]:
    register_user(client, email=email, role="recruiter")
    token = login_user(client, email=email)
    response = client.post(
        "/api/v1/jobs",
        headers=headers(token),
        json={
            "title": "Backend Engineer",
            "description": "Build and maintain FastAPI services.",
            "skills_json": ["python", "fastapi", "docker"],
            "seniority": "mid",
            "location": "London",
            "status": "open",
        },
    )
    assert response.status_code == 201
    return token, response.json()


def create_application(client: TestClient, *, candidate_email: str = "candidate@example.com") -> tuple[str, str, dict, dict]:
    recruiter_token, job = create_recruiter_job(client)
    candidate_token = create_candidate(client, email=candidate_email)
    response = client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job["id"]})
    assert response.status_code == 201
    return recruiter_token, candidate_token, job, response.json()


def start_session(client: TestClient, token: str, application_id: str) -> dict:
    response = client.post(
        "/api/v1/interviews/sessions",
        headers=headers(token),
        json={"application_id": application_id},
    )
    assert response.status_code == 201
    return response.json()


def test_candidate_can_start_interview_for_own_application(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    session = start_session(client, candidate_token, application["id"])

    assert session["application_id"] == application["id"]
    assert session["status"] == "in_progress"


def test_candidate_cannot_start_interview_for_another_candidates_application(client: TestClient) -> None:
    _, _, _, application = create_application(client, candidate_email="owner@example.com")
    other_token = create_candidate(client, email="other@example.com")

    response = client.post(
        "/api/v1/interviews/sessions",
        headers=headers(other_token),
        json={"application_id": application["id"]},
    )

    assert response.status_code == 403


def test_recruiter_can_view_interview_for_own_job_application(client: TestClient) -> None:
    recruiter_token, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])

    response = client.get(f"/api/v1/interviews/sessions/{session['id']}", headers=headers(recruiter_token))

    assert response.status_code == 200
    assert response.json()["id"] == session["id"]


def test_recruiter_cannot_view_unrelated_interview(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])
    register_user(client, email="other-recruiter@example.com", role="recruiter")
    other_recruiter_token = login_user(client, email="other-recruiter@example.com")

    response = client.get(f"/api/v1/interviews/sessions/{session['id']}", headers=headers(other_recruiter_token))

    assert response.status_code == 403


def test_generated_interview_has_questions(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    session = start_session(client, candidate_token, application["id"])

    assert len(session["questions"]) == 6


def test_question_generation_includes_technical_and_behavioral(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    session = start_session(client, candidate_token, application["id"])
    question_types = {question["question_type"] for question in session["questions"]}

    assert "technical" in question_types
    assert "behavioral" in question_types


def test_candidate_can_answer_own_question(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])
    question = session["questions"][0]

    response = client.post(
        f"/api/v1/interviews/questions/{question['id']}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I built a FastAPI project and improved API performance with clear results."},
    )

    assert response.status_code == 200
    assert response.json()["score"] is not None


def test_candidate_cannot_answer_another_candidates_question(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client, candidate_email="owner@example.com")
    session = start_session(client, candidate_token, application["id"])
    other_token = create_candidate(client, email="other@example.com")

    response = client.post(
        f"/api/v1/interviews/questions/{session['questions'][0]['id']}/answer",
        headers=headers(other_token),
        json={"answer_text": "I built a FastAPI project."},
    )

    assert response.status_code == 403


def test_answer_receives_score_and_feedback(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])

    response = client.post(
        f"/api/v1/interviews/questions/{session['questions'][0]['id']}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I built a Python FastAPI project, solved bugs, and improved the result."},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["score"] >= 0
    assert "summary" in data["feedback_json"]


def test_completing_session_calculates_overall_score(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])
    client.post(
        f"/api/v1/interviews/questions/{session['questions'][0]['id']}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I built a Python FastAPI project and improved the result."},
    )

    response = client.post(f"/api/v1/interviews/sessions/{session['id']}/complete", headers=headers(candidate_token))

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["overall_score"] is not None


def test_cannot_answer_after_session_completed(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])
    client.post(
        f"/api/v1/interviews/questions/{session['questions'][0]['id']}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I built a Python FastAPI project and improved the result."},
    )
    client.post(f"/api/v1/interviews/sessions/{session['id']}/complete", headers=headers(candidate_token))

    response = client.post(
        f"/api/v1/interviews/questions/{session['questions'][1]['id']}/answer",
        headers=headers(candidate_token),
        json={"answer_text": "I would answer this later."},
    )

    assert response.status_code == 409


def test_candidate_can_list_own_interviews(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    start_session(client, candidate_token, application["id"])

    response = client.get("/api/v1/interviews/me", headers=headers(candidate_token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_can_view_any_interview(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    session = start_session(client, candidate_token, application["id"])
    register_user(client, email="admin@example.com", role="admin")
    admin_token = login_user(client, email="admin@example.com")

    response = client.get(f"/api/v1/interviews/sessions/{session['id']}", headers=headers(admin_token))

    assert response.status_code == 200
    assert response.json()["id"] == session["id"]
