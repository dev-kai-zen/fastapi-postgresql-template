# Docker commands (this project)

Run all `docker compose` commands from the **repository root** (where `docker-compose.yaml` lives). Compose reads `.env` in that directory for variables such as `API_PUBLISH_PORT`, `POSTGRES_PUBLISH_PORT`, `REDIS_PUBLISH_PORT`, `POSTGRES_DB`, and JWT/Google settings required by the API container.

## Everyday workflow

| Goal | Command |
|------|---------|
| Start API, Postgres, and Redis (detached) | `docker compose up -d` |
| Start and rebuild images after Dockerfile or dependency changes | `docker compose up -d --build` |
| Stop containers (keep volumes) | `docker compose down` |
| Stop containers **and delete** named volumes (Postgres + Redis data) | `docker compose down -v` |
| Follow logs (all services) | `docker compose logs -f` |
| Logs for one service | `docker compose logs -f api` (or `database`, `redis`) |

After `up`, the API is available at `http://localhost:${API_PUBLISH_PORT}` (see `.env`). Default in many setups is port `8000` or whatever you set in `API_PUBLISH_PORT`.

## Build and run only some services

| Goal | Command |
|------|---------|
| Postgres + Redis only (no API container) | `docker compose up -d database redis` |
| Useful for local `uvicorn` with host `DATABASE_URL` / `REDIS_URL` pointing at published ports | Same as above, then run the app on the host |

Service names in this file: `database`, `redis`, `api`. The `migrate` service is profile-gated (see below).

## Database migrations (Alembic)

Migrations use the `migrate` service (not started by plain `docker compose up`).

```bash
docker compose --profile migrate run --rm migrate
```

Runs `python -m alembic upgrade head` with the same environment as the API (including `DATABASE_URL` to the `database` service). Ensure Postgres is up (`docker compose up -d database` or full stack).

## Inspect and debug

| Goal | Command |
|------|---------|
| Show running containers for this project | `docker compose ps` |
| Validate merged compose + env substitution | `docker compose config` |
| Open a shell in the API container | `docker compose exec api bash` (or `sh` if `bash` is missing) |
| Postgres shell | Use `POSTGRES_USER` and `POSTGRES_DB` from `.env` (see example below) |

```bash
# Example when .env has POSTGRES_USER=postgres and POSTGRES_DB=mydb
docker compose exec database psql -U postgres -d mydb
```

Container names (fixed in compose): `backend-postgres-database`, `backend-fastapi-postgresql-redis`, `backend-fastapi-postgresql-api`.

## Images and cache

| Goal | Command |
|------|---------|
| Rebuild API image without cache | `docker compose build --no-cache api` |
| Remove unused images (careful: global cleanup) | `docker image prune` |

## Volumes

Named volumes in this project: `fastapi_postgresql_pgdata`, `fastapi_postgresql_redisdata`.

- **Remove volumes** (destructive): `docker compose down -v`
- **When to do it:** You changed `POSTGRES_DB` and Postgres still has the old database only; you want a clean DB/Redis state for development.

Postgres creates the database in `POSTGRES_DB` only on **first initialization** of an empty data directory. If you change `POSTGRES_DB` in `.env` but keep the old volume, either run `down -v` and `up` again or create the new database manually inside Postgres.

## Environment notes for Docker

- The API container does **not** load a copied `.env` file; it uses variables injected by Compose (`x-api-environment`). Keep required keys in the project `.env` so Compose can substitute them.
- **Host** vs **container** URLs: on your machine, use `localhost` and **published** ports from `.env` (e.g. `DATABASE_URL=...@localhost:5435/...`). Inside Compose, the API uses hostname `database` and port `5432`, which Compose sets via `DATABASE_URL` in `x-api-environment`.

## Troubleshooting quick checks

1. **API exits on startup (DB errors):** `docker compose logs api` — confirm Postgres is healthy and `POSTGRES_DB` matches an existing database in the volume.
2. **Port already in use:** Change `API_PUBLISH_PORT`, `POSTGRES_PUBLISH_PORT`, or `REDIS_PUBLISH_PORT` in `.env` and `docker compose up -d` again.
3. **Stale code in container:** `docker compose up -d --build api`

For deeper Postgres and Redis setup, see `markdown/4. POSTGRES_DOCKER_GUIDE.md` and `markdown/5. REDIS_DOCKER_GUIDE.md`.
