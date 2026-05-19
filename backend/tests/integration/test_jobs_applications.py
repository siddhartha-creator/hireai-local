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


def job_payload(*, status: str = "open", title: str = "Backend Engineer") -> dict:
    return {
        "title": title,
        "description": "Build and maintain production FastAPI services.",
        "requirements_json": ["Python", "SQL"],
        "skills_json": ["python", "fastapi"],
        "seniority": "junior",
        "location": "London",
        "employment_type": "full_time",
        "salary_min": 30000,
        "salary_max": 45000,
        "status": status,
    }


def create_recruiter_job(client: TestClient, *, email: str = "recruiter@example.com", status: str = "open") -> tuple[str, dict]:
    register_user(client, email=email, role="recruiter")
    token = login_user(client, email=email)
    response = client.post("/api/v1/jobs", headers=headers(token), json=job_payload(status=status))
    assert response.status_code == 201
    return token, response.json()


def create_candidate(client: TestClient, *, email: str = "candidate@example.com") -> str:
    register_user(client, email=email, role="candidate")
    return login_user(client, email=email)


def test_recruiter_can_create_job(client: TestClient) -> None:
    _, job = create_recruiter_job(client)

    assert job["title"] == "Backend Engineer"
    assert job["status"] == "open"


def test_candidate_cannot_create_job(client: TestClient) -> None:
    token = create_candidate(client)

    response = client.post("/api/v1/jobs", headers=headers(token), json=job_payload())

    assert response.status_code == 403


def test_candidate_can_list_open_jobs(client: TestClient) -> None:
    create_recruiter_job(client, status="open")
    token = create_candidate(client)

    response = client.get("/api/v1/jobs", headers=headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "open"


def test_candidate_cannot_see_draft_jobs(client: TestClient) -> None:
    create_recruiter_job(client, status="draft")
    token = create_candidate(client)

    response = client.get("/api/v1/jobs", headers=headers(token))

    assert response.status_code == 200
    assert response.json() == []


def test_recruiter_can_update_own_job(client: TestClient) -> None:
    token, job = create_recruiter_job(client)

    response = client.put(
        f"/api/v1/jobs/{job['id']}",
        headers=headers(token),
        json={"title": "Updated Backend Engineer"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Backend Engineer"


def test_recruiter_cannot_update_another_recruiters_job(client: TestClient) -> None:
    _, job = create_recruiter_job(client, email="owner@example.com")
    register_user(client, email="other@example.com", role="recruiter")
    other_token = login_user(client, email="other@example.com")

    response = client.put(
        f"/api/v1/jobs/{job['id']}",
        headers=headers(other_token),
        json={"title": "Unauthorized Update"},
    )

    assert response.status_code == 403


def test_candidate_can_apply_to_open_job(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="open")
    token = create_candidate(client)

    response = client.post(
        "/api/v1/applications",
        headers=headers(token),
        json={"job_id": job["id"], "cover_letter": "I am interested."},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "submitted"


def test_candidate_cannot_apply_twice(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="open")
    token = create_candidate(client)
    payload = {"job_id": job["id"]}

    first_response = client.post("/api/v1/applications", headers=headers(token), json=payload)
    second_response = client.post("/api/v1/applications", headers=headers(token), json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["errors"][0]["code"] == "duplicate_application"


def test_candidate_cannot_apply_to_closed_job(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="closed")
    token = create_candidate(client)

    response = client.post("/api/v1/applications", headers=headers(token), json={"job_id": job["id"]})

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "job_not_open"


def test_candidate_can_view_own_applications(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="open")
    token = create_candidate(client)
    client.post("/api/v1/applications", headers=headers(token), json={"job_id": job["id"]})

    response = client.get("/api/v1/applications/me", headers=headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recruiter_can_view_applications_for_own_job(client: TestClient) -> None:
    recruiter_token, job = create_recruiter_job(client, status="open")
    candidate_token = create_candidate(client)
    client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job["id"]})

    response = client.get(f"/api/v1/applications/job/{job['id']}", headers=headers(recruiter_token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recruiter_cannot_view_applications_for_another_recruiters_job(client: TestClient) -> None:
    _, job = create_recruiter_job(client, email="owner@example.com", status="open")
    register_user(client, email="other@example.com", role="recruiter")
    other_token = login_user(client, email="other@example.com")

    response = client.get(f"/api/v1/applications/job/{job['id']}", headers=headers(other_token))

    assert response.status_code == 403


def test_admin_can_view_application_details(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="open")
    candidate_token = create_candidate(client)
    application = client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job["id"]}).json()
    register_user(client, email="admin@example.com", role="admin")
    admin_token = login_user(client, email="admin@example.com")

    response = client.get(f"/api/v1/applications/{application['id']}", headers=headers(admin_token))

    assert response.status_code == 200
    assert response.json()["id"] == application["id"]


def test_admin_can_view_all_applications(client: TestClient) -> None:
    _, job = create_recruiter_job(client, status="open")
    candidate_token = create_candidate(client)
    client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job["id"]})
    register_user(client, email="admin@example.com", role="admin")
    admin_token = login_user(client, email="admin@example.com")

    response = client.get("/api/v1/applications", headers=headers(admin_token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_deleting_job_archives_it(client: TestClient) -> None:
    token, job = create_recruiter_job(client, status="open")

    response = client.delete(f"/api/v1/jobs/{job['id']}", headers=headers(token))

    assert response.status_code == 200
    assert response.json()["status"] == "archived"
