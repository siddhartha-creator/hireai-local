# Development Roadmap

## Phase 1: Foundation

- Monorepo structure
- Docker Compose
- Backend foundation
- Frontend foundation
- PostgreSQL configuration
- Alembic setup
- Documentation

## Phase 2: Authentication and RBAC

- Registration and login
- JWT access tokens
- Password hashing
- Current user dependency
- Candidate, recruiter, admin role checks

## Phase 3: Profiles

- Candidate profiles
- Recruiter profiles
- Profile completion state

## Phase 4: Jobs and Applications

- Recruiter job posting
- Candidate application submission
- Application status tracking
- Recruiter-owned application review
- Soft job archiving

## Phase 5: Resume Upload and Parsing

- Local PDF/DOCX upload
- Text extraction
- Parsed skill and experience storage
- Primary resume selection
- Recruiter/admin metadata access rules

## Phase 6: Matching and Scoring

- Rule-based scoring
- Score explanations
- Recruiter candidate ranking
- Candidate self-service score view
- Future-ready matching engine abstraction

## Phase 7: AI Interview Simulator

- Rule-based question generation
- Interview sessions
- Candidate answers
- Basic answer scoring with feedback
- Overall interview score calculation
- Candidate, recruiter, and admin interview access rules
- Future-ready interview AI interfaces

## Phase 8: Dashboards and Analytics

- Recruiter dashboard analytics API
- Candidate dashboard analytics API
- Admin platform analytics API
- Activity timeline derived from applications, interviews, and scores
- Minimal login/register frontend flow
- Protected frontend routes and role-aware navigation
- Minimal dashboard, jobs, applications, interviews, and profile pages

## Phase 9: Testing, Optimization, Documentation

- Unit and integration tests
- Frontend tests
- OpenAPI cleanup
- Final report support
