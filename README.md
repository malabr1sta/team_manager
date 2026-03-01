# team_manager

## Alembic workflow

Use these commands for schema migrations:

- `alembic upgrade head` - apply all migrations.
- `alembic revision --autogenerate -m "message"` - create a new migration.
- `alembic downgrade -1` - rollback one migration.

For local migration checks you can override DB URL:

- `ALEMBIC_DATABASE_URL="sqlite+aiosqlite:///./alembic_dev.db" uv run alembic upgrade head`

Rules:

- Update ORM models and migration in the same change.
- Do not edit existing revision history after it is shared.

## Docker run flow (development)

First run on new machine:

- `docker compose up -d`
- `docker compose exec backend uv run alembic upgrade head`
- `docker compose exec backend uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`
- `docker compose watch`

Run services in background first:

- `docker compose up -d`

Apply migrations inside backend container:

- `docker compose exec backend uv run alembic upgrade head`

Create superuser for admin login (inside container):

- `docker compose exec backend uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`

Check schemas/tables (schema-aware mode):

- `docker compose exec db psql -U postgres -d team_manager_db -c "\dn"`
- `docker compose exec db psql -U postgres -d team_manager_db -c "\dt identity.*"`

Start file watcher in a separate terminal:

- `docker compose watch`

Optional checks:

- `docker compose ps`
- `docker compose logs -f backend`

Stop services:

- `docker compose down`

Reset database volume (clean start):

- `docker compose down -v`

## Environment modes

- `TEST=false` (default): production-like Postgres mode with schemas (`identity`, `teams`, `tasks`, `evaluations`, `scheduling`, `calendar`).
- `TEST=true`: test mode without PostgreSQL schemas (used for local tests/SQLite style flow).

Important: if you switch from `TEST=true` to `TEST=false`, reset the Docker volume and re-run migrations.

## Admin panel (sqladmin)

Admin panel URL:

- `http://localhost:8000/admin`

Login uses existing `identity` users.
Only users with `is_superuser=true` and active account can access admin.
Business role `admin` in domain logic does not grant admin-panel access.

Notes:

- Password is verified against stored `hashed_password`.
- Projection models are read-only in admin to keep event-driven consistency.

Create superuser for admin login:

- `uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`
- `docker compose exec backend uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`

## Minimal frontend (MVP)

Frontend entry point:

- `http://localhost:8000/ui/index.html`

Pages by context:

- `/ui/identity.html`
- `/ui/teams.html`
- `/ui/tasks.html`
- `/ui/evaluations.html`
- `/ui/scheduling.html`
- `/ui/calendar.html`

How to use:

- Register and login on `/ui/index.html` (JWT is stored in browser `localStorage`).
- Open a context page and call actions from forms/buttons.
- For team-scoped pages, enter `team_id` and load capabilities from:
  - `GET /api/v1/teams/{team_id}/capabilities/me`

Smoke scenario:

1. Login as user with team access.
2. Open `/ui/teams.html`, set `team_id`, click `Load capabilities`.
3. Verify buttons are disabled for actions with `false` capabilities.
4. Run allowed action (expect success) and forbidden action (expect readable `403`).
5. Check `/ui/tasks.html`, `/ui/scheduling.html`, `/ui/evaluations.html` with same team and confirm gating behavior.