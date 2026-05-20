# API Design Plan

All application routes are versioned under:

```text
/api/v1
```

Initial endpoints:

```text
GET /api/v1/health
GET /api/v1/auth/status
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
GET /api/v1/users/status
GET /api/v1/users/me
GET /api/v1/candidates/status
GET /api/v1/candidates/me
PUT /api/v1/candidates/me
GET /api/v1/candidates/{candidate_id}
GET /api/v1/recruiters/status
GET /api/v1/recruiters/me
PUT /api/v1/recruiters/me
GET /api/v1/recruiters/{recruiter_id}
GET /api/v1/resumes/status
POST /api/v1/resumes/upload
GET /api/v1/resumes/me
GET /api/v1/resumes/{resume_id}
GET /api/v1/resumes/{resume_id}/parsed
PUT /api/v1/resumes/{resume_id}/primary
DELETE /api/v1/resumes/{resume_id}
GET /api/v1/jobs/status
POST /api/v1/jobs
GET /api/v1/jobs
GET /api/v1/jobs/{job_id}
PUT /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
GET /api/v1/applications/status
POST /api/v1/applications
GET /api/v1/applications
GET /api/v1/applications/me
GET /api/v1/applications/job/{job_id}
GET /api/v1/applications/{application_id}
PUT /api/v1/applications/{application_id}/status
GET /api/v1/interviews/status
GET /api/v1/scoring/status
POST /api/v1/scoring/applications/{application_id}/score
GET /api/v1/scoring/applications/{application_id}
GET /api/v1/scoring/jobs/{job_id}
GET /api/v1/scoring/me
GET /api/v1/scoring
GET /api/v1/analytics/status
```

## Roles

Default roles:

```text
admin
recruiter
candidate
```

Role checks are enforced in backend dependencies. Frontend role state is display-only and must not be trusted for authorization.

## Auth Requests

Register:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "candidate@example.com",
  "full_name": "Candidate User",
  "password": "Password123!",
  "role": "candidate"
}
```

Login:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "candidate@example.com",
  "password": "Password123!"
}
```

Login response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "candidate@example.com",
    "full_name": "Candidate User",
    "is_active": true,
    "roles": [
      {
        "id": "uuid",
        "name": "candidate",
        "description": "Candidate user who can manage their profile and applications."
      }
    ]
  }
}
```

Current user:

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## RBAC Proof Endpoints

```text
GET /api/v1/recruiters/status
Allowed: admin, recruiter

GET /api/v1/candidates/status
Allowed: admin, candidate
```

## Profile APIs

Candidate profile:

```http
GET /api/v1/candidates/me
Authorization: Bearer <candidate_token>
```

```http
PUT /api/v1/candidates/me
Authorization: Bearer <candidate_token>
Content-Type: application/json

{
  "headline": "Backend Engineer",
  "summary": "FastAPI and PostgreSQL candidate.",
  "location": "London",
  "skills_json": ["python", "fastapi"],
  "education_json": [],
  "experience_json": [],
  "experience_years": 2,
  "portfolio_url": "https://example.com",
  "linkedin_url": "https://linkedin.com/in/example",
  "github_url": "https://github.com/example"
}
```

Recruiter profile:

```http
GET /api/v1/recruiters/me
Authorization: Bearer <recruiter_token>
```

```http
PUT /api/v1/recruiters/me
Authorization: Bearer <recruiter_token>
Content-Type: application/json

{
  "company_name": "HireAI Labs",
  "company_website": "https://example.com",
  "company_size": "11-50",
  "industry": "Recruitment Technology",
  "position": "Talent Lead",
  "phone": "+44 7000 000000",
  "location": "London",
  "company_description": "Local-first hiring platform research team."
}
```

Admin profile lookup:

```text
GET /api/v1/candidates/{candidate_id}
GET /api/v1/recruiters/{recruiter_id}
```

## Profile Completion

Candidate profile is completed when:

- `headline` exists
- `summary` exists
- `skills_json` has at least one skill
- `experience_years` is not null
- `location` exists

Recruiter profile is completed when:

- `company_name` exists
- `industry` exists
- `position` exists
- `location` exists

## Job APIs

Create job:

```http
POST /api/v1/jobs
Authorization: Bearer <recruiter_token>
Content-Type: application/json

{
  "title": "Backend Engineer",
  "description": "Build and maintain production FastAPI services.",
  "requirements_json": ["Python", "SQL"],
  "skills_json": ["python", "fastapi"],
  "seniority": "junior",
  "location": "London",
  "employment_type": "full_time",
  "salary_min": 30000,
  "salary_max": 45000,
  "status": "open"
}
```

List jobs:

```http
GET /api/v1/jobs
Authorization: Bearer <access_token>
```

Candidates only see `open` jobs. Recruiters see their own jobs. Admin users see all jobs.

Job statuses:

```text
draft
open
closed
archived
```

Employment types:

```text
full_time
part_time
internship
contract
remote
```

Deleting a job soft-deletes it by setting `status` to `archived`; applications are preserved.

## Application APIs

Apply to job:

```http
POST /api/v1/applications
Authorization: Bearer <candidate_token>
Content-Type: application/json

{
  "job_id": "uuid",
  "cover_letter": "I am interested in this role."
}
```

Candidate applications:

```http
GET /api/v1/applications/me
Authorization: Bearer <candidate_token>
```

Admin applications:

```http
GET /api/v1/applications
Authorization: Bearer <admin_token>
```

Recruiter job applications:

```http
GET /api/v1/applications/job/{job_id}
Authorization: Bearer <recruiter_token>
```

Update application status:

```http
PUT /api/v1/applications/{application_id}/status
Authorization: Bearer <recruiter_token>
Content-Type: application/json

{
  "status": "under_review"
}
```

Application statuses:

```text
submitted
under_review
shortlisted
rejected
accepted
withdrawn
```

Permission rules:

- Recruiters can create, update, and archive only their own jobs.
- Admin users can view/update/archive any job.
- Candidates can view and apply only to open jobs.
- Candidates cannot apply to the same job twice.
- Candidates can view only their own applications.
- Recruiters can view/update applications only for their own jobs.
- Admin users can view and update all applications.

## Resume APIs

Upload resume:

```http
POST /api/v1/resumes/upload
Authorization: Bearer <candidate_token>
Content-Type: multipart/form-data

file=<resume.pdf|resume.docx>
```

List candidate resumes:

```http
GET /api/v1/resumes/me
Authorization: Bearer <candidate_token>
```

Read resume metadata:

```http
GET /api/v1/resumes/{resume_id}
Authorization: Bearer <access_token>
```

Read parsed data:

```http
GET /api/v1/resumes/{resume_id}/parsed
Authorization: Bearer <access_token>
```

Mark primary:

```http
PUT /api/v1/resumes/{resume_id}/primary
Authorization: Bearer <candidate_token>
```

Delete:

```http
DELETE /api/v1/resumes/{resume_id}
Authorization: Bearer <candidate_token>
```

File restrictions:

- Allowed file types: `.pdf`, `.docx`
- Maximum size: 5MB
- Stored locally under `backend/storage/resumes/` by default through `RESUME_UPLOAD_DIR`
- API responses do not expose `file_path`

Parsing behavior:

- PDF text extraction uses `pypdf`
- DOCX text extraction uses `python-docx`
- Skill extraction uses rule-based keyword matching

Parsed resume data shape:

```json
{
  "skills": [],
  "education": [],
  "experience": [],
  "summary": "",
  "parser_version": "rule_based_v1"
}
```

Initial skill keywords include `python`, `fastapi`, `django`, `flask`, `javascript`, `typescript`, `react`, `next.js`, `node.js`, `express`, `sql`, `postgresql`, `mongodb`, `docker`, `git`, `aws`, `machine learning`, `nlp`, `data analysis`, `html`, `css`, and `tailwind`.

Resume permission rules:

- Candidates can upload, list, mark primary, delete, and view only their own resumes.
- Admin users can view any resume metadata and parsed data.
- Recruiters can view resume metadata and parsed data only for candidates who applied to their jobs.
- The first uploaded resume becomes primary automatically.
- Marking one resume primary unsets other primary resumes for that candidate.

## Scoring APIs

Trigger or recalculate score:

```http
POST /api/v1/scoring/applications/{application_id}/score
Authorization: Bearer <access_token>
```

Read application score:

```http
GET /api/v1/scoring/applications/{application_id}
Authorization: Bearer <access_token>
```

List scores for a job:

```http
GET /api/v1/scoring/jobs/{job_id}
Authorization: Bearer <recruiter_or_admin_token>
```

Candidate scores:

```http
GET /api/v1/scoring/me
Authorization: Bearer <candidate_token>
```

Admin all scores:

```http
GET /api/v1/scoring
Authorization: Bearer <admin_token>
```

Scoring formula:

```text
overall_score = skill_score + experience_score + education_score + location_score
skill_score:       50 points
experience_score:  25 points
education_score:   10 points
location_score:    15 points
```

Skill scoring compares `job.skills_json` with candidate profile `skills_json` and primary resume `extracted_skills_json`. If a job has no skills, neutral skill credit is 25/50.

Experience scoring uses seniority mapping:

```text
internship: 0 years
junior:     1 year
mid:        3 years
senior:     5 years
lead:       7 years
```

Missing or unknown seniority receives neutral experience credit of 10/25. Education receives 10 points when parsed resume education exists, otherwise 0. Location receives 15 for exact match or both remote, 5 for missing data, and 0 otherwise.

Explanation JSON example:

```json
{
  "summary": "Candidate is a strong match with score 95/100.",
  "skill_reason": "Matched 3 of 3 required skills. Missing: none.",
  "experience_reason": "Candidate has 5 years; mid expects about 3 years.",
  "education_reason": "Education evidence found in parsed resume.",
  "location_reason": "Candidate location matches job location.",
  "recommendation": "strong_match"
}
```

Recommendations:

```text
80+    strong_match
50-79  moderate_match
<50    weak_match
```

Scoring permission rules:

- Candidate can score/view only their own applications.
- Recruiter can score/view only applications for their own jobs.
- Admin can score/view all applications and scores.

This is `rule_based_v1`. The matching engine is isolated behind `MatchingEngineInterface`, so OpenAI, embeddings, or pgvector-based matching can replace it later without rewriting persistence or routers.

## Migrations

```bash
cd backend
alembic upgrade head
```

The migrations create:

```text
users
roles
user_roles
candidate_profiles
recruiter_profiles
jobs
applications
resumes
match_scores
```

It also inserts the default roles. A safe role seeder is available:

```bash
python -m app.utils.seed_roles
```

Planned response shape:

```json
{
  "data": {},
  "message": "Success",
  "request_id": "uuid",
  "errors": null
}
```

Planned error shape:

```json
{
  "data": null,
  "message": "Validation failed",
  "request_id": "uuid",
  "errors": [
    {
      "field": "email",
      "code": "invalid_email"
    }
  ]
}
```

Phase 7 will add the AI interview simulator.
