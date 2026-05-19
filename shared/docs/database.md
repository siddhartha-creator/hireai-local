# Database Design Plan

PostgreSQL is the source of truth. SQLAlchemy models define the current auth, profile, job, application, and resume entities, with placeholders for later AI workflows.

## Core Tables

- `users`
- `roles`
- `user_roles`
- `candidate_profiles`
- `recruiter_profiles`
- `resumes`
- `jobs`
- `applications`
- `match_scores`
- `interview_sessions`
- `interview_questions`
- `candidate_answers`
- `activity_logs`

## Design Notes

- UUID primary keys are used for public-facing entities.
- JSONB is used for flexible AI outputs and parsed resume data.
- Business-critical fields stay normalized.
- Alembic will own schema migrations.
- Future vector support can use `pgvector` or a separate ChromaDB service.

## Profile Tables

`candidate_profiles`:

```text
id
user_id
headline
summary
phone
location
skills_json
education_json
experience_json
experience_years
portfolio_url
linkedin_url
github_url
is_completed
created_at
updated_at
```

`recruiter_profiles`:

```text
id
user_id
company_name
company_website
company_size
industry
position
phone
location
company_description
is_completed
created_at
updated_at
```

Each profile table has a unique `user_id`, giving each user at most one profile of that type. Candidate and recruiter profiles are created automatically during registration for the matching role. Admin users do not need profiles.

Candidate completion requires `headline`, `summary`, at least one skill in `skills_json`, `experience_years`, and `location`.

Recruiter completion requires `company_name`, `industry`, `position`, and `location`.

## Job and Application Tables

`jobs`:

```text
id
recruiter_id
title
description
requirements_json
skills_json
seniority
location
employment_type
salary_min
salary_max
status
created_at
updated_at
```

Job status values:

```text
draft
open
closed
archived
```

Employment type values:

```text
full_time
part_time
internship
contract
remote
```

`applications`:

```text
id
job_id
candidate_id
status
cover_letter
applied_at
updated_at
```

Application status values:

```text
submitted
under_review
shortlisted
rejected
accepted
withdrawn
```

Each `(job_id, candidate_id)` pair is unique, preventing duplicate applications. Jobs are archived instead of hard-deleted so application history remains intact.

## Resume Table

`resumes`:

```text
id
candidate_id
file_name
original_file_name
file_path
file_type
file_size
extracted_text
parsed_data_json
extracted_skills_json
is_primary
uploaded_at
updated_at
```

Resume files are stored locally outside the Python source package under `backend/storage/resumes/` by default. The database stores the internal file path, but API responses omit it. Parsed data uses JSONB so later AI parsing can expand the structure without a migration.

`parsed_data_json` shape:

```json
{
  "skills": [],
  "education": [],
  "experience": [],
  "summary": "",
  "parser_version": "rule_based_v1"
}
```

Only one resume should be primary for a candidate at a time. The service layer enforces this by unsetting existing primary resumes before marking a new one primary.
