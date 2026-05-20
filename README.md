# HireAI Local

HireAI Local is a local-first AI interview and hiring platform for a production-grade Final Year Project. The current foundation includes backend authentication, role-based access control, candidate/recruiter profiles, job posting, application tracking, resume upload/parsing, and rule-based candidate-job scoring while keeping interviews, dashboards, and frontend screens out of scope until later phases.

## Services

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- AI layer: rule-based placeholders behind replaceable interfaces

## Run Locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

## Database Migrations

```bash
cd backend
alembic upgrade head
```

The migrations create auth, profile, job, application, resume, and match score tables, and insert the default roles:

- `admin`
- `recruiter`
- `candidate`

You can also seed roles idempotently from Python:

```bash
cd backend
python -m app.utils.seed_roles
```

## Backend Tests

```bash
cd backend
pip install -e ".[dev]"
pytest
```

## Authentication Endpoints

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/users/me
```

Protected RBAC proof endpoints:

```text
GET /api/v1/recruiters/status   recruiter or admin
GET /api/v1/candidates/status   candidate or admin
```

## Profile Endpoints

```text
GET /api/v1/candidates/me          candidate only
PUT /api/v1/candidates/me          candidate only
GET /api/v1/candidates/{id}        admin only

GET /api/v1/recruiters/me          recruiter only
PUT /api/v1/recruiters/me          recruiter only
GET /api/v1/recruiters/{id}        admin only
```

Candidate profiles are auto-created when a candidate registers. Recruiter profiles are auto-created when a recruiter registers. Admin users do not need profiles.

Candidate completion requires `headline`, `summary`, at least one skill in `skills_json`, `experience_years`, and `location`.

Recruiter completion requires `company_name`, `industry`, `position`, and `location`.

## Job and Application Endpoints

```text
POST   /api/v1/jobs                    recruiter/admin
GET    /api/v1/jobs                    authenticated users; candidates see open jobs only
GET    /api/v1/jobs/{job_id}           owner/admin, or candidates if open
PUT    /api/v1/jobs/{job_id}           owner/admin
DELETE /api/v1/jobs/{job_id}           owner/admin; archives instead of hard-deletes

POST /api/v1/applications              candidate only
GET  /api/v1/applications              admin only
GET  /api/v1/applications/me           candidate only
GET  /api/v1/applications/job/{job_id} recruiter owner/admin
GET  /api/v1/applications/{id}         candidate owner, recruiter job owner, or admin
PUT  /api/v1/applications/{id}/status  recruiter job owner/admin
```

Application status lifecycle:

```text
submitted -> under_review -> shortlisted -> accepted
submitted -> under_review -> rejected
submitted -> withdrawn
```

## Resume Endpoints

```text
POST   /api/v1/resumes/upload              candidate only
GET    /api/v1/resumes/me                  candidate only
GET    /api/v1/resumes/{resume_id}         owner, admin, or recruiter with related application
GET    /api/v1/resumes/{resume_id}/parsed  owner, admin, or recruiter with related application
PUT    /api/v1/resumes/{resume_id}/primary owner candidate only
DELETE /api/v1/resumes/{resume_id}         owner candidate only
```

Resume files are stored locally under `backend/storage/resumes/` by default through `RESUME_UPLOAD_DIR`. Only `.pdf` and `.docx` files are accepted, with a 5MB limit. API responses never expose raw file paths.

Parsing uses `pypdf` for PDFs, `python-docx` for DOCX files, and rule-based keyword extraction for initial skills.

## Scoring Endpoints

```text
POST /api/v1/scoring/applications/{application_id}/score  candidate owner, recruiter job owner, or admin
GET  /api/v1/scoring/applications/{application_id}        candidate owner, recruiter job owner, or admin
GET  /api/v1/scoring/jobs/{job_id}                        recruiter job owner or admin
GET  /api/v1/scoring/me                                   candidate only
GET  /api/v1/scoring                                      admin only
```

The scoring engine is deterministic `rule_based_v1`: skills contribute 50 points, experience 25, education 10, and location 15. If a candidate has no primary resume, scoring falls back to profile data and education receives 0.

Register:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"candidate@example.com\",\"full_name\":\"Candidate User\",\"password\":\"Password123!\",\"role\":\"candidate\"}"
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"candidate@example.com\",\"password\":\"Password123!\"}"
```

Current user:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Current Scope

Implemented:

- Monorepo structure
- Versioned FastAPI app
- Health endpoint
- PostgreSQL settings and SQLAlchemy session setup
- Alembic migration scaffold and initial auth migration
- Candidate/recruiter profile migration
- Jobs/applications migration
- Resume migration and local storage service
- Match scoring migration and rule-based matching engine
- Password hashing and JWT access tokens
- Registration, login, and current-user endpoints
- Role-based backend dependencies
- Candidate and recruiter profile APIs
- Job posting and application workflow APIs
- Resume upload, parsing, primary selection, and metadata access APIs
- Candidate-job match scoring APIs
- Placeholder module routers
- Database model placeholders
- Rule-based AI service interfaces
- Next.js/Tailwind frontend foundation
- Docker Compose for frontend, backend, and PostgreSQL
- Architecture documentation

Intentionally left as placeholders:

- Interview simulator UI
- Dashboards and analytics screens
- Frontend auth screens
