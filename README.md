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

Run services in background first:

- `docker compose up -d`

Start file watcher in a separate terminal:

- `docker compose watch`

Apply migrations inside backend container:

- `docker compose exec backend uv run alembic upgrade head`

Optional checks:

- `docker compose ps`
- `docker compose logs -f backend`

Stop services:

- `docker compose down`