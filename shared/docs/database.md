# Database Design Plan

PostgreSQL is the source of truth. SQLAlchemy models define the current auth, profile, job, application, resume, match scoring, and interview simulator entities.

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

## Match Score Table

`match_scores`:

```text
id
application_id
candidate_id
job_id
overall_score
skill_score
experience_score
education_score
location_score
explanation_json
matched_skills_json
missing_skills_json
scoring_version
created_at
updated_at
```

Each application has at most one match score. Recalculating an application score updates the existing row. `explanation_json`, `matched_skills_json`, and `missing_skills_json` are stored as JSONB so future OpenAI or embedding-based explanations can extend the payload.

## Interview Tables

`interview_sessions`:

```text
id
application_id
candidate_id
job_id
status
overall_score
feedback_json
started_at
completed_at
created_at
updated_at
```

Interview session status values:

```text
in_progress
completed
cancelled
```

`interview_questions`:

```text
id
session_id
question_text
question_type
skill_tag
expected_signals_json
order_index
created_at
```

Question type values:

```text
technical
behavioral
role_specific
resume_based
```

`candidate_answers`:

```text
id
question_id
answer_text
score
feedback_json
answered_at
created_at
updated_at
```

Each application can have many interview sessions. Each session has many generated questions. Each question has at most one candidate answer. `expected_signals_json` stores deterministic scoring hints, and `feedback_json` stores rule-based feedback for both answers and completed sessions. These JSONB columns keep the schema ready for later OpenAI-generated questions, rubrics, and richer feedback without forcing immediate table changes.
