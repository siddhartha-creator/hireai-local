# FYP Report Outline

## Abstract

Summarize HireAI Local as a local-first AI-assisted hiring platform with authentication, role-based workflows, resume parsing, matching, interview simulation, analytics, and Docker-based local deployment.

## Problem Statement

Recruitment workflows often require fragmented tools for resume review, candidate screening, interviews, and application tracking. Small teams and students also need a privacy-friendly local system for experimentation without cloud deployment.

## Objectives

- Build a SaaS-style hiring platform that runs locally.
- Support recruiter, candidate, and admin roles.
- Implement resume parsing, job matching, mock interviews, scoring, and analytics.
- Keep AI services modular for future OpenAI or embedding integration.
- Provide a production-style architecture using FastAPI, Next.js, PostgreSQL, SQLAlchemy, Alembic, and Docker Compose.

## Scope

Included:

- Authentication and RBAC
- Candidate/recruiter profiles
- Jobs and applications
- Resume upload/parsing
- Rule-based scoring
- Rule-based interview simulator
- Dashboard analytics
- Minimal protected frontend

Excluded:

- Cloud deployment
- OpenAI integration
- Email sending
- Realtime notifications
- Audio/video interviews

## Methodology

Describe phased development from backend foundation to profiles, jobs, resumes, scoring, interviews, analytics, frontend integration, and final hardening.

## System Architecture

Explain the monorepo, Docker Compose services, API versioning, backend module boundaries, service/repository pattern, and frontend feature-based structure.

## Database Design

Cover users, roles, profiles, jobs, applications, resumes, match scores, interview sessions, interview questions, candidate answers, and activity logs.

## Implementation

Discuss:

- JWT authentication
- Role-based API dependencies
- Local file storage
- Rule-based resume parsing and skill extraction
- Matching engine abstraction
- Interview generator/scorer abstraction
- Analytics aggregation
- Protected frontend routing

## Testing

Summarize backend unit/integration tests, frontend component tests, build checks, and Docker configuration validation.

## Results

Show screenshots or demo observations for recruiter dashboard, candidate dashboard, admin analytics, scoring results, and interview results.

## Limitations

- Rule-based AI logic is deterministic and simpler than LLM-based reasoning.
- Frontend supports minimal viewing workflows, not full CRUD editing.
- Activity logging is seeded for demo and ready for broader workflow integration.
- Localhost deployment only.

## Future Work

Reference `shared/docs/future-work.md`.

## Conclusion

Conclude that HireAI Local demonstrates a production-style, local-first hiring platform foundation with modular AI boundaries and a clean path to advanced AI features.
