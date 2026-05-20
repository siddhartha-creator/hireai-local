# Final Demo Script

This flow demonstrates HireAI Local end to end without Docker, using local PostgreSQL on Windows.

## 1. Start PostgreSQL

Open Windows Services and confirm the PostgreSQL service is running, or use:

```powershell
Get-Service *postgres*
```

## 2. Ensure Database Exists

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\backend
.venv\Scripts\activate
python -m app.utils.ensure_database
```

If the `hireai` role cannot log in, open pgAdmin or `psql` as a PostgreSQL superuser and run:

```sql
CREATE ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
ALTER ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
CREATE DATABASE hireai_local OWNER hireai;
```

## 3. Run Migrations

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\backend
alembic upgrade head
```

If `alembic` is not on PATH:

```powershell
python -m alembic upgrade head
```

## 4. Seed Demo Data

```powershell
python -m app.utils.seed_demo_data
```

Demo accounts:

```text
admin@hireai.local / Password123!
recruiter@hireai.local / Password123!
candidate@hireai.local / Password123!
```

## 5. Start Backend

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```text
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/docs
```

## 6. Start Frontend

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

## 7. Recruiter Creates Job

1. Login as `recruiter@hireai.local`.
2. Open `/recruiter/dashboard` and show analytics cards.
3. Open `/recruiter/jobs`.
4. Click `Create job`.
5. Create a job with skills such as `python, fastapi, postgresql, docker`.
6. Open the created job detail page.
7. Explain that applications and scores will appear here.

## 8. Candidate Uploads Resume

1. Logout.
2. Login as `candidate@hireai.local`.
3. Open `/candidate/resumes`.
4. Upload a small PDF or DOCX resume.
5. Show extracted skills and parsed resume JSON.

## 9. Candidate Applies to Job

1. Open `/candidate/jobs`.
2. Select the recruiter-created open job.
3. Add a short cover letter.
4. Click `Apply to job`.
5. The app redirects to `/candidate/applications/[id]`.

## 10. Candidate Generates Score

1. On the candidate application detail page, click `Generate score`.
2. Show overall score, score breakdown, and matched skills.

## 11. Candidate Starts Interview

1. Click `Start interview`.
2. The app opens `/candidate/interviews/[id]`.
3. Show generated technical, behavioral, resume-based, or role-specific questions.

## 12. Candidate Answers Questions

1. Type an answer for one or more questions.
2. Click `Submit answer`.
3. Show per-answer score and feedback.
4. Click `Complete interview`.
5. Show final overall interview score.

## 13. Recruiter Reviews Application

1. Logout.
2. Login as `recruiter@hireai.local`.
3. Open `/recruiter/jobs`.
4. Select the job.
5. Open the candidate application.
6. Show match score and interview sessions.
7. Click `Recalculate score` if needed.

## 14. Admin Views Platform Analytics

1. Logout.
2. Login as `admin@hireai.local`.
3. Open `/admin/dashboard`.
4. Show platform totals for users, candidates, recruiters, jobs, applications, and interviews.

## 15. Swagger Backup

Use `http://127.0.0.1:8000/docs` if the frontend is unavailable. Useful endpoints:

```text
POST /api/v1/auth/login
GET  /api/v1/analytics/recruiter/dashboard
GET  /api/v1/analytics/candidate/dashboard
GET  /api/v1/analytics/platform
POST /api/v1/scoring/applications/{application_id}/score
POST /api/v1/interviews/sessions
POST /api/v1/interviews/questions/{question_id}/answer
POST /api/v1/interviews/sessions/{session_id}/complete
```
