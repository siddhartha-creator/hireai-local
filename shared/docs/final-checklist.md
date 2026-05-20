# Final Submission Checklist

## Environment

- [ ] PostgreSQL service is running.
- [ ] Database `hireai_local` exists.
- [ ] User `hireai` can connect with password `root1`.
- [ ] `backend/.env` contains `DATABASE_URL=postgresql+psycopg://hireai:root1@localhost:5432/hireai_local`.
- [ ] Frontend uses `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

## Backend

- [ ] `python -m app.utils.ensure_database` succeeds.
- [ ] `python -m alembic upgrade head` succeeds.
- [ ] `python -m alembic heads` shows one head.
- [ ] `python -m alembic current` shows the current revision.
- [ ] `python -m app.utils.seed_demo_data` succeeds.
- [ ] `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` starts.
- [ ] Health check opens: `http://127.0.0.1:8000/api/v1/health`.
- [ ] Swagger opens: `http://127.0.0.1:8000/docs`.

## Frontend

- [ ] `npm install` has been run.
- [ ] `npm run dev` starts.
- [ ] Frontend opens: `http://localhost:3000`.
- [ ] Login page shows demo credentials.
- [ ] Logout works.
- [ ] Wrong-role pages are blocked by protected route checks and backend RBAC.

## Tests

- [ ] Backend tests pass: `python -m pytest`.
- [ ] Frontend tests pass: `npm test -- --run`.
- [ ] Frontend build passes: `npm run build`.

## Demo Accounts

- [ ] `admin@hireai.local / Password123!` works.
- [ ] `recruiter@hireai.local / Password123!` works.
- [ ] `candidate@hireai.local / Password123!` works.

## Recruiter Flow

- [ ] Recruiter dashboard loads.
- [ ] Recruiter can create a job.
- [ ] Recruiter can view own jobs.
- [ ] Recruiter can view applications for a job.
- [ ] Recruiter can view/recalculate match score.
- [ ] Recruiter can view interview sessions for an application.

## Candidate Flow

- [ ] Candidate dashboard loads.
- [ ] Candidate can browse open jobs.
- [ ] Candidate can upload a PDF/DOCX resume.
- [ ] Candidate can view parsed resume data.
- [ ] Candidate can apply to a job.
- [ ] Candidate can generate/view match score.
- [ ] Candidate can start an interview.
- [ ] Candidate can answer questions.
- [ ] Candidate can complete an interview and view final score.

## Admin Flow

- [ ] Admin dashboard loads.
- [ ] Platform analytics show users, candidates, recruiters, jobs, applications, and interviews.

## Viva Preparation

- [ ] Read `shared/docs/viva-questions.md`.
- [ ] Prepare screenshots for dashboards, scoring, resume upload, and interview flow.
- [ ] Prepare explanation of why rule-based AI was used first.
- [ ] Prepare future-work explanation for OpenAI and embeddings.
