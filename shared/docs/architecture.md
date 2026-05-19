# System Architecture

HireAI Local is structured as a modular monolith with clean boundaries. This keeps Phase 1 simple enough for local development while preserving the shape of a real SaaS hiring platform.

## Dependency Direction

```text
API Router -> Service -> Repository -> Database
              Service -> AI Interface
              Service -> Activity Logger
```

Rules:

- Routers stay thin and only handle HTTP concerns.
- Services own business logic and orchestration.
- Repositories own persistence.
- AI services never write directly to the database.
- Frontend role state is never trusted for authorization.
- Backend dependencies will enforce JWT identity and role checks in Phase 2.

## Backend Structure

```text
backend/app/
  main.py
  core/          settings, database, security, exceptions, logging
  api/v1/        versioned routers
  modules/       domain modules and replaceable services
  models/        SQLAlchemy models
  schemas/       Pydantic DTOs
  repositories/  persistence abstractions
  services/      business service base classes
```

## Frontend Structure

```text
frontend/src/
  app/           Next.js app router
  components/    reusable UI, layout, forms
  features/      feature modules
  lib/           API client, auth helpers, validators, constants
  hooks/         shared hooks
  stores/        auth and app state stores
  types/         shared TypeScript interfaces
  styles/        global styles
```

## AI Boundary

The `ai_services` module starts with rule-based implementations:

- `RuleBasedResumeParser`
- `RuleBasedMatchingEngine`
- `RuleBasedInterviewQuestionGenerator`

Future OpenAI or local LLM providers should implement the same interfaces.
