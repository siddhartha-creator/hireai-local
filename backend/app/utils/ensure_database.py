from __future__ import annotations

import sys

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import settings


def ensure_database_exists(database_url: str | None = None) -> None:
    target_url = make_url(database_url or settings.sqlalchemy_database_uri)
    database_name = target_url.database
    if not database_name:
        raise RuntimeError("DATABASE_URL must include a database name.")

    maintenance_databases = ["postgres", "template1"]
    errors: list[str] = []

    try:
        for maintenance_database in maintenance_databases:
            maintenance_url = target_url.set(drivername="postgresql", database=maintenance_database)
            safe_maintenance_url = maintenance_url.render_as_string(hide_password=True)
            try:
                with psycopg.connect(maintenance_url.render_as_string(hide_password=False), autocommit=True) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                        if cursor.fetchone():
                            print(f'Database "{database_name}" already exists.')
                            return
                        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
                        print(f'Database "{database_name}" created.')
                        return
            except psycopg.OperationalError as exc:
                errors.append(f"{safe_maintenance_url}: {exc}")
                continue
        raise RuntimeError(
            "Could not connect to a PostgreSQL maintenance database.\n"
            + "\n".join(errors)
            + "\nCheck that PostgreSQL is running, port 5432 is reachable, and the username/password are correct."
        )
    except psycopg.OperationalError as exc:
        raise RuntimeError(
            "Could not connect to PostgreSQL maintenance database.\n"
            f"Attempted: {target_url.set(drivername='postgresql', database='postgres').render_as_string(hide_password=True)}\n"
            "Check that PostgreSQL is running, port 5432 is reachable, and the username/password are correct."
        ) from exc
    except psycopg.errors.InsufficientPrivilege as exc:
        raise RuntimeError(
            f'User "{target_url.username}" does not have permission to create database "{database_name}".\n'
            "Create it manually with psql or pgAdmin, or grant CREATEDB to the user."
        ) from exc


def main() -> None:
    try:
        ensure_database_exists()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
