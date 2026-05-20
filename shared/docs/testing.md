# Testing Guide

## Backend Tests

Run from the backend directory:

```bash
cd backend
python -m pytest
```

Coverage includes:

- Auth and RBAC
- Candidate/recruiter profiles
- Jobs and applications
- Resume upload/parsing
- Matching and scoring
- Interview generation/scoring
- Analytics aggregation
- Demo seed idempotency

## Frontend Tests

Run from the frontend directory:

```bash
cd frontend
npm test -- --run
```

Coverage includes:

- Home page rendering
- Login flow and token persistence
- Protected route redirect
- Dashboard rendering with mocked APIs
- Empty dashboard activity state
- Demo credential hints

## Frontend Build

```bash
cd frontend
npm run build
```

This verifies TypeScript, App Router pages, and production compilation.

## Docker Validation

Run from the repository root:

```bash
docker compose config
```

This validates the Compose file without starting containers. If Docker Desktop is not running or unavailable, document the failure and validate backend/frontend tests locally.

## Recommended Final Check Sequence

```bash
cd backend
python -m pytest

cd ..\frontend
npm test -- --run
npm run build

cd ..
docker compose config
```
