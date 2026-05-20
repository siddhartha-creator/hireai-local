# HireAI Local

HireAI Local is a local-first AI interview and hiring platform for a production-grade Final Year Project. The current foundation includes backend authentication, role-based access control, candidate/recruiter profiles, job posting, application tracking, resume upload/parsing, rule-based candidate-job scoring, a rule-based AI interview simulator, dashboard analytics APIs, and minimal protected frontend flows.

## Services

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- AI layer: rule-based placeholders behind replaceable interfaces

## Run Locally

Docker remains supported:

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

## Run Without Docker: Local PostgreSQL Setup on Windows

Use this path when Docker Desktop is unavailable and PostgreSQL is installed directly on Windows.

Local PostgreSQL target:

```text
Host: localhost
Port: 5432
Database: hireai_local
Username: hireai
Password: root1
DATABASE_URL: postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
```

Create the database in pgAdmin or `psql`:

```sql
CREATE ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
CREATE DATABASE hireai_local;
ALTER USER hireai WITH PASSWORD 'root1';
```

If the role already exists, run:

```sql
ALTER ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
CREATE DATABASE hireai_local OWNER hireai;
```

Create or update `backend\.env`:

```env
PROJECT_NAME=HireAI Local
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
JWT_SECRET_KEY=replace-with-a-local-secret
BACKEND_CORS_ORIGINS=http://localhost:3000
RESUME_UPLOAD_DIR=storage/resumes
```

Run the backend:

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\backend

python -m venv .venv
.venv\Scripts\activate

pip install -e .

python -m app.utils.ensure_database

alembic upgrade head

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `alembic` is not recognized:

```powershell
python -m alembic upgrade head
```

Run the frontend:

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\frontend
npm install
npm run dev
```

Verification URLs:

```text
Backend health: http://127.0.0.1:8000/api/v1/health
Swagger docs:    http://127.0.0.1:8000/docs
Frontend:        http://localhost:3000
```

Detailed guide: `shared/docs/local-postgresql-setup.md`.

## Final Demo Setup

For the final non-Docker demo:

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local
```

Backend terminal:

```powershell
cd backend
python -m app.utils.ensure_database
python -m alembic upgrade head
python -m app.utils.seed_demo_data
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend terminal:

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\frontend
npm install
npm run dev
```

Demo accounts:

```text
admin@hireai.local / Password123!
recruiter@hireai.local / Password123!
candidate@hireai.local / Password123!
```

Recommended walkthrough: `shared/docs/demo-script.md`.

## Database Migrations

```bash
cd backend
alembic upgrade head
```

The migrations create auth, profile, job, application, resume, match score, and interview tables, and insert the default roles:

- `admin`
- `recruiter`
- `candidate`

You can also seed roles idempotently from Python:

```bash
cd backend
python -m app.utils.seed_roles
```

Seed demo data idempotently:

```bash
cd backend
python -m app.utils.seed_demo_data
```

The demo seeder creates the three demo accounts, completed candidate/recruiter profiles, three jobs, two applications, resume metadata, a match score, a completed interview, and activity log entries. Running it twice will not duplicate the demo records.

## Backend Tests

```bash
cd backend
pip install -e ".[dev]"
pytest
```

## Frontend Tests and Build

```bash
cd frontend
npm install
npm test -- --run
npm run build
```

## Troubleshooting

- If `alembic` is not recognized on Windows, use `python -m alembic upgrade head` from the backend virtual environment.
- If login succeeds but dashboards are empty, run `python -m app.utils.seed_demo_data`.
- If Docker is not running, `docker compose` commands will fail until Docker Desktop is started.
- If frontend API calls fail, confirm `NEXT_PUBLIC_API_URL` points to `http://localhost:8000/api/v1`.
- If PostgreSQL says `password authentication failed`, connect as a PostgreSQL superuser and run `ALTER ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;`.
- If PostgreSQL says `database "hireai_local" does not exist`, run `CREATE DATABASE hireai_local OWNER hireai;`.
- If port `5432` is already in use, check `netstat -ano | findstr :5432` and update `DATABASE_URL` if PostgreSQL uses another port.
- If you see a `psycopg` driver error, run `pip install -e .` from the backend virtual environment.
- If Alembic cannot find `DATABASE_URL`, run it from the `backend` directory and confirm `backend\.env` exists.

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

## Interview Endpoints

```text
POST /api/v1/interviews/sessions                      candidate owner, recruiter job owner, or admin
GET  /api/v1/interviews/sessions/{session_id}         candidate owner, recruiter job owner, or admin
POST /api/v1/interviews/sessions/{session_id}/complete candidate owner only
GET  /api/v1/interviews/me                            candidate only
GET  /api/v1/interviews/applications/{application_id} candidate owner, recruiter job owner, or admin
GET  /api/v1/interviews                               admin only
POST /api/v1/interviews/questions/{question_id}/answer candidate owner only
```

Interview statuses:

```text
in_progress
completed
cancelled
```

The interview engine is deterministic `rule_based_v1`: it generates six questions from job skills, candidate skills, resume skills, job context, and any existing match score. Answers are scored out of 10 using completeness, expected keyword overlap, role relevance, and evidence of practical experience. Completing a session stores an overall score out of 100.

## Analytics Endpoints

```text
GET /api/v1/analytics/recruiter/dashboard  recruiter only
GET /api/v1/analytics/candidate/dashboard  candidate only
GET /api/v1/analytics/platform             admin only
```

Recruiter analytics aggregate only recruiter-owned jobs, applications, match scores, interview scores, requested skills, and recent activity. Candidate analytics aggregate only the current candidate's applications, status breakdown, match scores, interview scores, matched skills, and activity timeline. Platform analytics give admin-level totals for users, candidates, recruiters, jobs, applications, interviews, and average match score.

## Frontend Routes

Public:

```text
/
/login
/register
```

Candidate:

```text
/candidate/dashboard
/candidate/jobs
/candidate/jobs/{id}
/candidate/applications
/candidate/applications/{id}
/candidate/resumes
/candidate/interviews
/candidate/interviews/{id}
/candidate/profile
```

Recruiter:

```text
/recruiter/dashboard
/recruiter/jobs
/recruiter/jobs/new
/recruiter/jobs/{id}
/recruiter/applications
/recruiter/applications/{id}
/recruiter/interviews
/recruiter/profile
```

Admin:

```text
/admin/dashboard
```

Frontend authentication uses local access-token persistence, a React auth context, current-user hydration through `/api/v1/auth/me`, client-side protected route guards, and role-aware sidebar navigation. Backend RBAC remains the source of truth.

## API Response Notes

Domain and validation errors use a consistent error envelope:

```json
{
  "data": null,
  "message": "Validation failed",
  "request_id": "uuid",
  "errors": []
}
```

Successful endpoints currently return typed resource bodies directly. This is documented as an intentional Phase 9 choice to avoid breaking completed tests and frontend integrations late in the submission cycle. A future API polish phase can wrap all success responses in `{ "data": ..., "message": "...", "errors": null }`.

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
- Interview migration and rule-based interview simulator APIs
- Dashboard analytics APIs
- Activity log migration and demo activity seed data
- Password hashing and JWT access tokens
- Registration, login, and current-user endpoints
- Role-based backend dependencies
- Candidate and recruiter profile APIs
- Job posting and application workflow APIs
- Resume upload, parsing, primary selection, and metadata access APIs
- Candidate-job match scoring APIs
- Interview session, question generation, answer scoring, and completion APIs
- Minimal frontend login, registration, protected routes, role navigation, dashboards, and read-only resource pages
- Timezone-aware timestamp defaults
- Idempotent demo seed data
- Placeholder module routers
- Database model placeholders
- Rule-based AI service interfaces
- Next.js/Tailwind frontend foundation
- Docker Compose for frontend, backend, and PostgreSQL
- Architecture documentation

Intentionally left as placeholders:

- Full dashboard CRUD workflows and advanced analytics visuals
- Frontend profile/job/application/interview editors
- Live activity logging across every production workflow
