# Viva Questions and Suggested Answers

## Why Did You Choose This Project?

Hiring platforms combine authentication, roles, file handling, workflow state, scoring, interviews, and analytics. That made the project suitable for demonstrating full-stack engineering and AI-system design without relying on cloud services.

## Why FastAPI?

FastAPI gives type-driven request validation, automatic OpenAPI documentation, dependency injection, and strong async/file-upload support. It fits Python-based AI services naturally and keeps API code concise.

## Why PostgreSQL?

PostgreSQL is reliable for relational business data and also supports JSON fields, which are useful for parsed resumes, scoring explanations, and interview feedback. It can later support vector search through `pgvector`.

## Why Rule-Based AI First?

Rule-based services are deterministic, testable, and runnable offline. They let the architecture prove the workflow first. The AI interfaces mean OpenAI or embeddings can replace the rule-based logic later without changing routers or persistence.

## How Is This Different From a CRUD App?

It has end-to-end hiring workflows: resume upload/parsing, candidate-job scoring, generated interview questions, answer scoring, role-aware analytics, and protected recruiter/candidate/admin journeys. The services contain business rules rather than just database forms.

## How Does RBAC Work?

Users have roles through a `user_roles` association table. JWTs include role names, but backend dependencies still load the current user and enforce role checks. The frontend only uses roles for navigation, not authorization.

## How Does Resume Parsing Work?

The backend stores uploaded PDF/DOCX files locally, extracts text using local parsing libraries, then applies keyword-based skill extraction. Parsed fields are stored as JSON so the structure can expand later.

## How Does Matching Score Work?

The score is out of 100: skills 50, experience 25, education 10, and location 15. It compares job skills with candidate profile and resume skills, maps seniority to years of experience, checks parsed education, and compares location. The result includes matched skills, missing skills, and explanation JSON.

## How Does Interview Scoring Work?

The system generates about six questions from job skills, candidate skills, resume skills, and role context. Answers are scored out of 10 using completeness, expected keyword overlap, relevance, and practical evidence. Completing a session averages answered scores and converts them to a 100-point overall score.

## What Are the Main Limitations?

The AI is rule-based, resume parsing is basic, the frontend is intentionally minimal, activity logging is not wired into every live action, and the system is designed for localhost rather than production cloud deployment.

## How Would You Add OpenAI Later?

I would implement new classes behind the existing matching and interview interfaces, add prompt templates and structured output schemas, keep database writes inside services, and add tests with mocked OpenAI responses.

## How Would You Deploy It?

Package backend and frontend containers, use managed PostgreSQL, configure environment-specific secrets, run Alembic migrations in CI/CD, serve the frontend behind HTTPS, and add observability/logging.

## How Would You Scale It?

Separate background parsing/scoring work into workers, add queues, cache analytics, index frequent queries, store large files outside the app container, and add pgvector or ChromaDB for semantic search.

## How Do You Ensure Security?

Passwords are hashed, JWTs are signed, protected routes use backend dependencies, RBAC is enforced server-side, resume paths are not exposed, upload types and sizes are validated, and environment variables hold secrets.

## What Tests Did You Write?

Backend integration tests cover auth/RBAC, profiles, jobs, applications, resumes, scoring, interviews, analytics, and seed data. Backend unit tests cover rule-based engines. Frontend tests cover login, protected route behavior, dashboard rendering, resume upload view, job list, and interview page rendering.

## Why Use Alembic?

Alembic gives versioned database migrations. It lets the schema evolve safely and makes setup repeatable for the final demo.

## What Would You Improve With More Time?

OpenAI-backed parsing/interviews, semantic matching with embeddings, richer recruiter workflows, email notifications, fairness checks, real deployment, and more complete activity logging.
