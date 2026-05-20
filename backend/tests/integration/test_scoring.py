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


def create_candidate(client: TestClient, *, email: str = "candidate@example.com", strong: bool = True) -> str:
    register_user(client, email=email, role="candidate")
    token = login_user(client, email=email)
    if strong:
        payload = {
            "headline": "Backend Engineer",
            "summary": "Python FastAPI developer.",
            "location": "London",
            "skills_json": ["python", "fastapi"],
            "experience_years": 5,
        }
    else:
        payload = {
            "headline": "New Candidate",
            "summary": "Learning HTML.",
            "location": "Manchester",
            "skills_json": ["html"],
            "experience_years": 0,
        }
    response = client.put("/api/v1/candidates/me", headers=headers(token), json=payload)
    assert response.status_code == 200
    return token


def create_recruiter_job(client: TestClient, *, email: str = "recruiter@example.com", strong: bool = True) -> tuple[str, dict]:
    register_user(client, email=email, role="recruiter")
    token = login_user(client, email=email)
    payload = {
        "title": "Backend Engineer",
        "description": "Build FastAPI systems.",
        "skills_json": ["python", "fastapi"],
        "seniority": "mid" if strong else "senior",
        "location": "London",
        "status": "open",
    }
    response = client.post("/api/v1/jobs", headers=headers(token), json=payload)
    assert response.status_code == 201
    return token, response.json()


def apply_to_job(client: TestClient, candidate_token: str, job_id: str) -> dict:
    response = client.post("/api/v1/applications", headers=headers(candidate_token), json={"job_id": job_id})
    assert response.status_code == 201
    return response.json()


def create_application(client: TestClient, *, strong: bool = True) -> tuple[str, str, dict, dict]:
    recruiter_token, job = create_recruiter_job(client, strong=strong)
    candidate_token = create_candidate(client, strong=strong)
    application = apply_to_job(client, candidate_token, job["id"])
    return recruiter_token, candidate_token, job, application


def test_candidate_can_score_own_application(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    assert response.status_code == 200
    assert response.json()["score"]["application_id"] == application["id"]


def test_recruiter_can_score_application_for_own_job(client: TestClient) -> None:
    recruiter_token, _, _, application = create_application(client)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(recruiter_token))

    assert response.status_code == 200


def test_recruiter_cannot_score_another_recruiters_job_application(client: TestClient) -> None:
    _, _, _, application = create_application(client)
    register_user(client, email="other@example.com", role="recruiter")
    other_token = login_user(client, email="other@example.com")

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(other_token))

    assert response.status_code == 403


def test_admin_can_score_any_application(client: TestClient) -> None:
    _, _, _, application = create_application(client)
    register_user(client, email="admin@example.com", role="admin")
    admin_token = login_user(client, email="admin@example.com")

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(admin_token))

    assert response.status_code == 200


def test_score_includes_overall_and_breakdown(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))
    data = response.json()

    assert response.status_code == 200
    assert "overall_score" in data["score"]
    assert data["breakdown"]["skill_score"] >= 0
    assert data["explanation"]["recommendation"] in ["strong_match", "moderate_match", "weak_match"]


def test_matched_and_missing_skills_are_correct(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))
    score = response.json()["score"]

    assert score["matched_skills_json"] == ["fastapi", "python"]
    assert score["missing_skills_json"] == []


def test_score_updates_if_recalculated(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    first = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token)).json()
    second = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token)).json()

    assert first["score"]["id"] == second["score"]["id"]


def test_candidate_can_view_own_scores(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)
    client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    response = client.get("/api/v1/scoring/me", headers=headers(candidate_token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recruiter_can_list_scores_for_own_job(client: TestClient) -> None:
    recruiter_token, candidate_token, job, application = create_application(client)
    client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    response = client.get(f"/api/v1/scoring/jobs/{job['id']}", headers=headers(recruiter_token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_candidate_cannot_list_scores_for_job(client: TestClient) -> None:
    _, candidate_token, job, application = create_application(client)
    client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    response = client.get(f"/api/v1/scoring/jobs/{job['id']}", headers=headers(candidate_token))

    assert response.status_code == 403


def test_scoring_works_without_resume_using_profile_only(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    assert response.status_code == 200
    assert response.json()["score"]["education_score"] == 0


def test_recommendation_strong_match_for_high_score(client: TestClient) -> None:
    _, candidate_token, _, application = create_application(client, strong=True)

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(candidate_token))

    assert response.json()["score"]["overall_score"] >= 80
    assert response.json()["score"]["explanation_json"]["recommendation"] == "strong_match"


def test_recommendation_weak_match_for_low_score(client: TestClient) -> None:
    recruiter_token, job = create_recruiter_job(client, strong=False)
    candidate_token = create_candidate(client, strong=False)
    application = apply_to_job(client, candidate_token, job["id"])

    response = client.post(f"/api/v1/scoring/applications/{application['id']}/score", headers=headers(recruiter_token))

    assert response.json()["score"]["overall_score"] < 50
    assert response.json()["score"]["explanation_json"]["recommendation"] == "weak_match"
