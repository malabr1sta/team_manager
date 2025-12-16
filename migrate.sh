docker compose exec backend /app/.venv/bin/alembic upgrade head
docker exec -it team_manager /app/.venv/bin/alembic upgrade head
