# Local PostgreSQL Setup on Windows

Use this guide when Docker Desktop is unavailable and PostgreSQL is installed directly on Windows.

## Target Connection

```text
Host: localhost
Port: 5432
Database: hireai_local
Username: hireai
Password: root1
DATABASE_URL: postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
```

## 1. Install PostgreSQL

Install PostgreSQL for Windows from the official PostgreSQL installer. During installation, remember the password for the `postgres` superuser. This project uses a local role named:

```text
hireai
```

## 2. Check PostgreSQL Service

Open Windows Services and confirm the PostgreSQL service is running. It is usually named like:

```text
postgresql-x64-16
```

You can also check from PowerShell:

```powershell
Get-Service *postgres*
```

## 3. Create Database

Open pgAdmin or `psql` and run:

```sql
CREATE ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
CREATE DATABASE hireai_local;
ALTER USER hireai WITH PASSWORD 'root1';
```

If the `hireai` role already exists, use:

```sql
ALTER ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
CREATE DATABASE hireai_local OWNER hireai;
```

If the database already exists, keep it and only verify the password and owner.

## 4. Test Connection with psql

```powershell
psql -h localhost -p 5432 -U hireai -d hireai_local
```

When prompted, enter:

```text
root1
```

## 5. Configure Backend Environment

Create or update:

```text
C:\Users\khatr\Documents\FYP\hireai-local\backend\.env
```

Minimum local config:

```env
PROJECT_NAME=HireAI Local
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
JWT_SECRET_KEY=replace-with-a-local-secret
BACKEND_CORS_ORIGINS=http://localhost:3000
RESUME_UPLOAD_DIR=storage/resumes
```

`DATABASE_URL` takes precedence over the individual `POSTGRES_*` settings.

## 6. Install and Run Backend

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\backend

python -m venv .venv
.venv\Scripts\activate

pip install -e .

python -m app.utils.ensure_database

alembic upgrade head

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `alembic` is not recognized, use:

```powershell
python -m alembic upgrade head
```

## 7. Install and Run Frontend

```powershell
cd C:\Users\khatr\Documents\FYP\hireai-local\frontend
npm install
npm run dev
```

## 8. Verification URLs

```text
Backend health: http://127.0.0.1:8000/api/v1/health
Swagger docs:    http://127.0.0.1:8000/docs
Frontend:        http://localhost:3000
```

## Troubleshooting

### password authentication failed

The password in `DATABASE_URL` does not match the PostgreSQL `hireai` user password. Connect as a PostgreSQL superuser, then run:

```sql
ALTER ROLE hireai WITH LOGIN PASSWORD 'root1' CREATEDB;
```

Then retry migrations.

### database does not exist

Create the database:

```sql
CREATE DATABASE hireai_local;
```

If creating it as a superuser:

```sql
CREATE DATABASE hireai_local OWNER hireai;
```

### port 5432 already in use

Another PostgreSQL instance may already be running. Check:

```powershell
netstat -ano | findstr :5432
```

Either stop the conflicting service or update `DATABASE_URL` with the correct port.

### psycopg driver error

Install backend dependencies from the backend directory:

```powershell
pip install -e .
```

The project uses the `psycopg` driver, so the URL format is:

```text
postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
```

### Alembic cannot find DATABASE_URL

Confirm `backend\.env` exists and contains:

```env
DATABASE_URL=postgresql+psycopg://hireai:root1@localhost:5432/hireai_local
```

Run Alembic from the backend directory.

### frontend cannot reach backend

Confirm the backend is running at:

```text
http://127.0.0.1:8000
```

Confirm frontend `.env.example` or runtime env uses:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```
