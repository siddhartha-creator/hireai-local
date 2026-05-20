# Architecture Summary

HireAI Local is a local-first SaaS-style hiring platform built as a monorepo.

```text
hireai-local/
  backend/   FastAPI, SQLAlchemy, Alembic, pytest
  frontend/  Next.js, TypeScript, Tailwind, Vitest
  shared/    documentation, contracts, diagrams
```

## Backend

The backend follows a modular service architecture:

```text
Router -> Service -> Repository -> Database
          Service -> AI Interface
          Service -> Activity Logger
```

Routers are thin and only handle HTTP concerns. Services own business rules such as profile completion, application permissions, scoring, interview completion, and analytics aggregation. Repositories own database access. AI-like behavior is behind interfaces so rule-based implementations can later be replaced by OpenAI or embedding services.

## Frontend

The frontend uses feature-based organization:

```text
Page -> Feature View -> API Wrapper -> API Client
Page -> Protected Route -> Auth Context
```

The auth context stores the access token, loads the current user, handles logout, and supports protected route checks. Role-aware navigation improves usability, but backend RBAC remains the source of truth.

## Database

PostgreSQL stores core relational data:

- users and roles
- candidate and recruiter profiles
- jobs and applications
- resumes
- match scores
- interview sessions/questions/answers
- activity logs

JSON fields are used for flexible parsed data, extracted skills, explanations, feedback, and expected interview signals.

## AI Layer

The current AI layer is deterministic:

- rule-based resume skill extraction
- rule-based candidate-job matching
- rule-based question generation
- rule-based answer scoring

This makes the system testable and demo-ready offline. The interfaces provide a clean path to OpenAI, embeddings, or pgvector.

## Local Infrastructure

The system supports both:

- Docker Compose with PostgreSQL
- Local PostgreSQL on Windows without Docker

Alembic manages schema migrations, and the demo seed script creates repeatable demo accounts and workflow data.
