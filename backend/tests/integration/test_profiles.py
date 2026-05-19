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


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_candidate_profile_auto_created_after_registration(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.get("/api/v1/candidates/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["is_completed"] is False


def test_recruiter_profile_auto_created_after_registration(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = client.get("/api/v1/recruiters/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["is_completed"] is False


def test_candidate_can_get_own_profile(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.get("/api/v1/candidates/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["user_id"]


def test_candidate_can_update_own_profile(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.put(
        "/api/v1/candidates/me",
        headers=auth_headers(token),
        json={
            "headline": "Backend Engineer",
            "summary": "FastAPI and PostgreSQL candidate.",
            "location": "London",
            "skills_json": ["python", "fastapi"],
            "experience_years": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["headline"] == "Backend Engineer"
    assert data["is_completed"] is True


def test_candidate_cannot_access_recruiter_profile_endpoint(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.get("/api/v1/recruiters/me", headers=auth_headers(token))

    assert response.status_code == 403


def test_recruiter_can_get_own_profile(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = client.get("/api/v1/recruiters/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["user_id"]


def test_recruiter_can_update_own_profile(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = client.put(
        "/api/v1/recruiters/me",
        headers=auth_headers(token),
        json={
            "company_name": "HireAI Labs",
            "industry": "Recruitment Technology",
            "position": "Talent Lead",
            "location": "London",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "HireAI Labs"
    assert data["is_completed"] is True


def test_recruiter_cannot_access_candidate_profile_endpoint(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = client.get("/api/v1/candidates/me", headers=auth_headers(token))

    assert response.status_code == 403


def test_profile_completion_becomes_true_when_required_fields_are_filled(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    incomplete_response = client.put(
        "/api/v1/candidates/me",
        headers=auth_headers(token),
        json={"headline": "Backend Engineer"},
    )
    complete_response = client.put(
        "/api/v1/candidates/me",
        headers=auth_headers(token),
        json={
            "headline": "Backend Engineer",
            "summary": "Builds APIs.",
            "location": "London",
            "skills_json": ["python"],
            "experience_years": 1,
        },
    )

    assert incomplete_response.status_code == 200
    assert incomplete_response.json()["is_completed"] is False
    assert complete_response.status_code == 200
    assert complete_response.json()["is_completed"] is True


def test_admin_can_access_profile_by_id(client: TestClient) -> None:
    register_user(client, email="admin@example.com", role="admin")
    register_user(client, email="candidate@example.com", role="candidate")
    candidate_token = login_user(client, email="candidate@example.com")
    admin_token = login_user(client, email="admin@example.com")
    candidate_profile = client.get("/api/v1/candidates/me", headers=auth_headers(candidate_token)).json()

    response = client.get(
        f"/api/v1/candidates/{candidate_profile['id']}",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == candidate_profile["id"]
