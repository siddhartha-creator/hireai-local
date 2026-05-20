# FYP Report Outline

## Abstract

Present HireAI Local as a local-first AI-assisted hiring platform that supports recruiter, candidate, and admin workflows. Summarize the implemented modules: authentication, RBAC, profiles, jobs, applications, resume parsing, candidate-job scoring, mock interviews, analytics, and minimal protected frontend. Mention that AI is currently deterministic/rule-based and intentionally abstracted for later OpenAI or embedding integration.

## Introduction

Introduce hiring as a multi-step process involving profile collection, resume review, job matching, interview preparation, and candidate evaluation. Explain why a local-first system is useful for academic demonstration, privacy, and repeatable development without cloud dependency.

## Problem Statement

Recruitment tools are often fragmented across job boards, resume parsers, spreadsheets, interview notes, and analytics dashboards. Many student projects reduce hiring to CRUD screens and do not demonstrate realistic architecture, authorization, file handling, scoring logic, or end-to-end workflow visibility.

## Objectives

- Build a SaaS-style hiring platform that runs locally.
- Support three roles: admin, recruiter, and candidate.
- Implement secure JWT authentication and backend-enforced RBAC.
- Allow recruiters to create jobs and review applications.
- Allow candidates to manage profiles, upload resumes, apply to jobs, generate scores, and complete mock interviews.
- Provide deterministic AI-like services behind replaceable interfaces.
- Provide dashboard analytics and a demo-ready frontend.
- Use production-style tooling: FastAPI, Next.js, PostgreSQL, SQLAlchemy, Alembic, pytest, Vitest, and Docker Compose support.

## Scope

Included:

- Local PostgreSQL setup and Docker Compose support
- Authentication and RBAC
- Candidate/recruiter profiles
- Job posting and application tracking
- PDF/DOCX resume upload and parsing
- Rule-based skill extraction
- Rule-based candidate-job matching
- Rule-based interview question generation and answer scoring
- Recruiter, candidate, and admin analytics
- Demo seed data and minimal frontend flows

Excluded:

- OpenAI integration
- Cloud deployment
- Email invitations
- Realtime notifications
- Audio/video interview recording
- Advanced UI design system
- Multi-tenant recruiter teams

## Literature and Technology Review

Discuss:

- Applicant Tracking Systems and common recruitment workflows.
- Resume parsing approaches: rule-based parsing, keyword matching, NLP, and LLM extraction.
- Matching approaches: exact skill matching, weighted scoring, embeddings, and recommender systems.
- FastAPI as a Python API framework with type hints and OpenAPI support.
- PostgreSQL as a relational database with JSON support.
- Next.js as a React framework for frontend routing and app structure.
- Docker Compose as repeatable local infrastructure, with local PostgreSQL as a fallback for demonstration.

## System Architecture

Explain the monorepo:

```text
frontend/  Next.js UI
backend/   FastAPI API
shared/    documentation and contracts
```

Backend dependency direction:

```text
API Router -> Service -> Repository -> Database
              Service -> AI Interface
              Service -> Activity Logger
```

Frontend dependency direction:

```text
Page -> Feature View -> API Wrapper -> API Client
Page -> Protected Route -> Auth Context
```

Mention versioned APIs under `/api/v1`, centralized settings, Alembic migrations, and modular AI interfaces.

## Database Design

Explain the major entities:

- `users`, `roles`, `user_roles`
- `candidate_profiles`, `recruiter_profiles`
- `jobs`, `applications`
- `resumes`
- `match_scores`
- `interview_sessions`, `interview_questions`, `candidate_answers`
- `activity_logs`

Explain why UUIDs are used, why JSON fields are used for parsed/AI-like outputs, and why normalized tables are used for core business relationships.

## Implementation

Cover:

- JWT login and password hashing
- Backend RBAC dependencies
- Profile auto-creation after registration
- Recruiter job creation and application review
- Candidate application workflow
- Local resume storage and parser services
- Matching engine formula and explanation JSON
- Interview generator/scorer logic
- Analytics aggregation services
- Frontend auth context and protected routing
- Demo seed data and local PostgreSQL support

## Testing

Summarize:

- Backend unit tests for deterministic scoring/interview engines
- Backend integration tests for auth, RBAC, profiles, jobs, applications, resumes, scoring, interviews, analytics, and seed data
- Frontend tests for login, protected routes, dashboards, job list, resume upload view, and interview page rendering
- Build validation through `npm run build`
- Alembic head/current checks

## Results

Include screenshots or observations for:

- Login page with demo credentials
- Recruiter dashboard
- Job creation page
- Candidate resume upload
- Candidate application score
- Interview session with scored answers
- Admin analytics dashboard

## Limitations

- AI behavior is deterministic and rule-based, not LLM-powered.
- Resume parsing is keyword-oriented and not robust against all resume formats.
- Frontend is intentionally minimal for demonstration.
- Activity logs are seeded and partially structured but not wired into every live workflow.
- Deployment is localhost-focused.

## Future Work

Reference `shared/docs/future-work.md` and discuss:

- OpenAI integration
- Embeddings and pgvector
- Bias/fairness checks
- Email notifications
- Realtime updates
- Audio/video interview support
- Cloud deployment

## Conclusion

Conclude that HireAI Local demonstrates a complete, locally runnable hiring platform with realistic architecture, role-aware workflows, file handling, scoring, interviews, analytics, tests, and documentation. Emphasize that it is more than CRUD because it models end-to-end hiring decisions through modular services and explainable scoring.
