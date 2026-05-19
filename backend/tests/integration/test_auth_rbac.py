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


def login_user(client: TestClient, *, email: str, password: str = "Password123!") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_candidate(client: TestClient) -> None:
    data = register_user(client, email="candidate@example.com", role="candidate")

    assert data["email"] == "candidate@example.com"
    assert data["full_name"] == "Candidate User"
    assert data["roles"][0]["name"] == "candidate"
    assert "hashed_password" not in data


def test_duplicate_email_rejected(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "candidate@example.com",
            "full_name": "Duplicate User",
            "password": "Password123!",
            "role": "candidate",
        },
    )

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "email_exists"


def test_login_success(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": "Password123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "candidate@example.com"


def test_login_invalid_password_rejected(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "invalid_credentials"


def test_auth_me_works_with_token(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "candidate@example.com"


def test_users_me_requires_authenticated_user(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_recruiter_route_rejects_candidate(client: TestClient) -> None:
    register_user(client, email="candidate@example.com", role="candidate")
    token = login_user(client, email="candidate@example.com")

    response = client.get("/api/v1/recruiters/status", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["errors"][0]["code"] == "insufficient_role"


def test_recruiter_route_allows_recruiter(client: TestClient) -> None:
    register_user(client, email="recruiter@example.com", role="recruiter")
    token = login_user(client, email="recruiter@example.com")

    response = client.get("/api/v1/recruiters/status", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"module": "recruiters", "status": "ready"}
