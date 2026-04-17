# FastAPI API with Docker

## Two ways to run the stack (important)

| Where the API runs | Postgres / Redis hostname in URLs | Typical use |
| ------------------ | ----------------------------------- | ----------- |
| **On your machine** (venv + `uvicorn`) | `localhost` + **published** ports from `.env` (`POSTGRES_PUBLISH_PORT`, `REDIS_PUBLISH_PORT`) | Fast reload while coding |
| **In Compose** (API container) | **Compose service names** as hostnames: `database`, `redis`; DB port **5432**, Redis **6379** (inside the Docker network) | Closer to production, one command for full stack |

Use **one `.env`** if you like, but the **connection strings must match the layout you actually run**. The examples below show both patterns.

---

## Step 1 — `Dockerfile` (API image)

Create a `Dockerfile` in the **project root** (next to `docker-compose.yaml`).

This example assumes:

- Package layout: `app/main.py` with `app = FastAPI()`.
- Dependencies in `requirements.txt`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Piece | Purpose |
| ----- | ------- |
| `WORKDIR /app` | App code lives here inside the image |
| `COPY app ./app` | Your `app` Python package |
| `--host 0.0.0.0` | Required so the port is reachable **outside** the container |
| `8000` | HTTP port inside the container (map a different **host** port if you like) |

**Production:** use a pinned base image digest, non-root user, and multi-stage builds as your team requires; this is a minimal teaching baseline.

---

## Step 2 — Build and run the API image alone (optional)

From the project root:

```bash
docker build -t backend-api .
```

Run it (example: talk to Postgres/Redis already published on the **host** — URLs use `host.docker.internal` on Docker Desktop; on **Linux** you may need `extra_hosts` or use host gateway — simplest for Linux is running DB/Redis in Compose and the API in Compose too; see Step 4).

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://postgres:password@host.docker.internal:5435/fastapi_crud" \
  -e REDIS_URL="redis://:sample_password@host.docker.internal:6380/0" \
  backend-api
```

Adjust user, password, db name, ports, and Redis URL to match your `.env`. If Redis has no password, use `redis://host.docker.internal:6380/0`.


---

## Step 3 — Environment variables the API needs

Your FastAPI app (via Pydantic `BaseSettings` or `os.environ`) should read at least:

| Variable | Purpose |
| -------- | ------- |
| `DATABASE_URL` | SQLAlchemy / Psycopg URL |
| `REDIS_URL` | `redis` client URL (if you use Redis) |

**Password in Redis URL** (no username): `redis://:YOUR_PASSWORD@HOST:PORT/0`

---

## Step 4 — Add the API service to `docker-compose.yaml`

When **all services** run in the same Compose project, containers reach each other by **service name**:

- Postgres service: **`database`** (matches your file) → host `database`, port **5432**
- Redis service: **`redis`** → host `redis`, port **6379**

Example URLs **inside** the API container (replace values with your real `POSTGRES_*` and `REDIS_PASSWORD`):

```env
DATABASE_URL=postgresql+psycopg://postgres:password@database:5432/fastapi_crud
REDIS_URL=redis://:sample_password@redis:6379/0
```

Your [docker-compose.yaml](docker-compose.yaml) already sets Redis with `--requirepass ${REDIS_PASSWORD}`, so **`REDIS_URL` must include that password** when connecting from the API.

### Example `api` service (fragment)

Add under `services:` (same file as `database` and `redis`):

```yaml
  api:
    build: .
    container_name: fastapi-api
    ports:
      - "${API_PUBLISH_PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - database
      - redis
```

Notes:

- **`depends_on`** does not wait until Postgres is “ready”; for production you add healthchecks or retry logic in the app.
- **`environment:`** here uses Compose substitution from `.env`. Ensure `POSTGRES_PASSWORD` and special characters are safe for URLs (encode if needed).
- **`API_PUBLISH_PORT`** — add to `.env` / [.env.example](.env.example) if you want a configurable host port (default `8000`).

### Commands

```bash
docker compose up -d --build
```

Logs:

```bash
docker compose logs -f api
```

Open Swagger: `http://localhost:8000/docs` (or `http://localhost:${API_PUBLISH_PORT}/docs` if you changed the mapping).

---

## Step 5 — `.env` when the API runs on the host vs in Compose

You can keep **both** styles documented in comments, but only one pair should be “active” for a given run.

**API on host** (see [POSTGRES_DOCKER.md](POSTGRES_DOCKER.md), [REDIS_DOCKER.md](REDIS_DOCKER.md)):

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5435/fastapi_crud
REDIS_URL=redis://:sample_password@localhost:6380/0
```

**API in Compose** (use **service names**, internal ports):

```env
DATABASE_URL=postgresql+psycopg://postgres:password@database:5432/fastapi_crud
REDIS_URL=redis://:sample_password@redis:6379/0
```

If you inject URLs only via `docker-compose.yaml` `environment:` and not from a single `DATABASE_URL` line in `.env`, that is fine — avoid duplicating secrets in two places unless they stay in sync.

---

## Step 6 — Stop / rebuild

```bash
docker compose stop api
docker compose up -d --build api
```

Remove API container (Compose manages names):

```bash
docker compose rm -sf api
```

---

## Quick reference

| Topic | Detail |
| ----- | ------ |
| **Uvicorn target** | `app.main:app` when `main.py` defines `app` inside package `app` |
| **Listen address** | `0.0.0.0` inside the container |
| **Compose DB host** | Service name `database`, port `5432` |
| **Compose Redis host** | Service name `redis`, port `6379` |
| **Host machine** | `localhost` + published ports `POSTGRES_PUBLISH_PORT` / `REDIS_PUBLISH_PORT` |
| **Redis + password** | `redis://:password@host:port/0` |

If the API cannot connect, verify: URLs match **where** the API runs (host vs container), Redis password matches `--requirepass`, and Postgres credentials match `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`.
