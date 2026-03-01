# Team Manager (MVP)

Backend-приложение для управления командой внутри компании: пользователи, команды, задачи, оценки, встречи, календарь и админка.

Проект реализован как single-app MVP (без микросервисов), в стиле DDD с event-driven синхронизацией между bounded contexts.

## 1) Стек технологий

- **Backend:** `Python 3.13`, `FastAPI`, `Uvicorn`.
- **Авторизация и безопасность:** `fastapi-users`, `JWT`.
- **Данные и миграции:** `SQLAlchemy`, `Alembic`, `PostgreSQL` (основная БД), `SQLite` (тестовый режим).
- **Валидация и конфигурация:** `Pydantic`, `pydantic-settings`.
- **Админка:** `sqladmin`.
- **Frontend (MVP):** статический `HTML/CSS/JavaScript` (без тяжелого фреймворка).
- **Тесты и инструменты:** `pytest`, `coverage`, `uv`, `Docker`, `Docker Compose`.

## 2) Описание функционала

- Регистрация/логин пользователей (`fastapi-users`, JWT).
- Профиль пользователя: просмотр, изменение, удаление аккаунта.
- Команды: создание, просмотр состава, добавление/удаление участников, смена ролей.
- Задачи: создание, назначение исполнителя, изменение статуса, комментарии.
- Оценки: оценка выполненных задач по шкале `1..5`, список и средняя оценка за период.
- Встречи: создание, добавление/удаление участников, отмена.
- Календарь: дневной и месячный вид событий (задачи + встречи).
- Админка (`sqladmin`) с доступом только для `is_superuser`.
- Минимальный frontend для ручной проверки функционала MVP.

## 3) Архитектура (DDD + Event-Driven)

### Bounded contexts

- `identity`
- `teams`
- `tasks`
- `evaluations`
- `scheduling`
- `calendar`

### Слои

- **Domain**: `models.py`, `management.py` (бизнес-правила и проверки прав).
- **Application**: `use_cases.py` (оркестрация сценариев).
- **Infrastructure**: `orm_models.py`, `repository.py`, `unit_of_work.py`, `mappers.py`.
- **Integration**: события и handlers для межконтекстной синхронизации.

### Принципы

- Права проверяются в доменной логике.
- Роутеры остаются тонкими (`DTO -> UseCase -> UoW -> Domain`).
- Изменения в одном контексте распространяются в другие через events + handlers.

## 4) Структура проекта

```text
app/
  admin/              # sqladmin: auth, panel, views
  calendar/           # календарные проекции и API
  core/               # shared ядро, events, handlers registry
  deps/               # DI зависимости/UoW factories
  evaluations/        # оценки
  frontend/           # минимальный UI (html/js/css)
  identity/           # пользователи и auth
  routers/            # API роутеры по контекстам
  scheduling/         # встречи
  scripts/            # служебные скрипты (create_superuser)
  tasks/              # задачи и комментарии
  teams/              # команды и роли
  main.py             # entrypoint FastAPI
alembic/              # миграции БД
tests/                # unit/integration/shared tests
compose.yaml          # docker compose
Dockerfile            # backend image
```

## 5) Установка и запуск

### Локально (без Docker)

1. Установить зависимости:
   - `uv sync`
2. Настроить `.env` (см. `.env.example`).
3. Применить миграции:
   - `uv run alembic upgrade head`
4. Запустить сервер:
   - `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Docker (рекомендуемый flow)

1. В `.env` установить `TEST=false`.
2. Собрать и поднять контейнеры:
   - `docker compose up -d`
3. Применить миграции внутри backend:
   - `docker compose exec backend uv run alembic upgrade head`
4. Запустить watcher:
   - `docker compose watch`

Полезные команды:

- Логи backend: `docker compose logs -f backend`
- Статус сервисов: `docker compose ps`
- Остановка: `docker compose down`
- Полный сброс БД (удаление volume): `docker compose down -v`

## 6) Переменные окружения и режимы

- `TEST=false` — основной режим (PostgreSQL + схемы `identity/teams/tasks/evaluations/scheduling/calendar`).
- `TEST=true` — тестовый режим (обычно без схем, удобен для локальных тестов).

Важно: перед запуском тестов переключайте `TEST=true`, перед Docker/dev запуском возвращайте `TEST=false`.

## 7) Миграции Alembic

- Применить миграции: `uv run alembic upgrade head`
- Создать миграцию: `uv run alembic revision --autogenerate -m "message"`
- Откатить на 1 шаг: `uv run alembic downgrade -1`

Для Docker:

- `docker compose exec backend uv run alembic upgrade head`

Проверка схем/таблиц в Postgres:

- `docker compose exec db psql -U postgres -d team_manager_db -c "\dn"`
- `docker compose exec db psql -U postgres -d team_manager_db -c "\dt identity.*"`

## 8) Тестирование

Перед тестами установите в `.env`:

- `TEST=true`

Запуск:

- Все тесты: `uv run pytest`
- Точечно: `uv run pytest tests/teams/test_integration.py -q`

После тестов для обычного запуска верните:

- `TEST=false`

## 9) Покрытие тестами (без frontend)

```bash
uv run coverage erase
uv run coverage run -m pytest
uv run coverage report -m --omit="app/frontend/*"
```

- Общий процент смотрите в строке `TOTAL`.
- HTML-отчет:
  - `uv run coverage html --omit="app/frontend/*"`
  - открыть `htmlcov/index.html`.

## 10) Документация по API

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Базовый префикс API: `/api/v1`

Основные группы endpoint-ов:

- `auth` / `users` (identity)
- `teams`
- `tasks`
- `evaluations`
- `scheduling`
- `calendar`

## 11) Примеры запросов и ответов

### Регистрация

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!","username":"user1"}'
```

Ответ (пример):

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user1",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "deleted": false
}
```

### Логин

```bash
curl -X POST "http://localhost:8000/api/v1/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Password123!"
```

Ответ (пример):

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Текущий пользователь (`/users/me`)

```bash
curl "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <TOKEN>"
```

Ответ (пример, без `hashed_password`):

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user1",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "deleted": false
}
```

### Создание команды

```bash
curl -X POST "http://localhost:8000/api/v1/teams" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"team_name":"Core Team"}'
```

### Capabilities для текущего пользователя в команде

```bash
curl "http://localhost:8000/api/v1/teams/1/capabilities/me" \
  -H "Authorization: Bearer <TOKEN>"
```

### Создание задачи

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"team_id":1,"title":"Prepare report","description":"Q1","deadline":"2026-03-10T12:00:00+00:00"}'
```

### Календарь за день

```bash
curl "http://localhost:8000/api/v1/calendar/day?day=2026-03-10" \
  -H "Authorization: Bearer <TOKEN>"
```

## 12) Админ-панель

- URL: `http://localhost:8000/admin`
- Доступ только для пользователей с `is_superuser=true`.
- Роль `admin` в бизнес-домене не дает доступ в админку автоматически.
- `create/delete` в админке отключены для безопасной работы с event-driven логикой.

Создание superuser:

- Локально:
  - `uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`
- В Docker:
  - `docker compose exec backend uv run python -m app.scripts.create_superuser --email admin@example.com --password StrongPass123! --username admin`

## 13) Минимальный frontend

Frontend предназначен для ручной проверки MVP, а не для production-использования.

- Единая точка входа: `http://localhost:8000/` (редирект на `/ui/index.html`)
- Страницы контекстов:
  - `/ui/identity.html`
  - `/ui/teams.html`
  - `/ui/tasks.html`
  - `/ui/evaluations.html`
  - `/ui/scheduling.html`
  - `/ui/calendar.html`

Как работает:

- JWT сохраняется в `localStorage`.
- Доступность действий в UI определяется серверным endpoint-ом capabilities.
- UI скрывает/блокирует недоступные действия, но источник истины — backend проверки.

## 14) Что можно улучшить

- Ввести единообразную пагинацию во всех list endpoint-ах (где еще не покрыто).
- Добавить безопасные admin-actions через use-cases (вместо прямого ORM-редактирования), чтобы не нарушать бизнес-логику и event-chain.
- Расширить API контрактными тестами и e2e smoke-тестами.
- Добавить CI-пайплайн с порогом покрытия.
- Улучшить frontend (валидация, уведомления, UX), сохранив server-driven permissions.
