# PostgreSQL with Docker (custom host port)

## Step 1 — Pick a free host port

To check which ports are already in use on your computer:

_Terminal_

```
# On Linux or macOS:
sudo lsof -iTCP -sTCP:LISTEN -Pn

# On Windows (in Command Prompt):
netstat -ano | findstr LISTENING

# Or to specifically check for 5432 (the Postgres default):
sudo lsof -iTCP:5432 -sTCP:LISTEN -Pn

# On Windows (in Command Prompt):
netstat -ano | findstr :5432
```

Choose any unused TCP port on your computer, for example:

- `5435`

The examples below use **`5435`**. Replace it if that port is taken.

---

## Step 2 — Run PostgreSQL in Docker

This creates a named container with a user, password, and database. The **container** listens on `5432`; your **host** uses `5435`.

```bash
docker run --name postgres-database \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=fastapi_crud \
  -p 5435:5432 \
  -d postgres:16
```

| Flag / env                            | Purpose                                  |
| ------------------------------------- | ---------------------------------------- |
| `--name postgres-database`             | Stable name for start/stop/logs          |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | Login for your app                       |
| `POSTGRES_DB`                         | Default database name                    |
| `-p 5435:5432`                        | **Host 5435** → **container 5432**       |
| `-d`                                  | Run in background                        |
| `postgres:16`                         | Image tag (adjust version if you prefer) |

**Security:** use strong passwords outside local learning. Never commit real credentials.

---

## Step 3 — Confirm (and start if needed) the container

Check if your container is running:

```bash
docker ps --filter name=postgres-database
```

If nothing shows up (not running), start it:

```bash
docker start postgres-database
```

Then check again:

```bash
docker ps --filter name=postgres-database
```

You should see the container **UP** and ports like `0.0.0.0:5435->5432/tcp`.

---

## Step 4 — Test a connection (host port)

From the host, talk to Postgres on **`localhost:5435`** (not 5432):

Change the POSTGRES_USER & POSTGRES_DB with your user and db name:

```bash
docker exec -it postgres-database psql -U POSTGRES_USER -d POSTGRES_DB -c "SELECT version();"
```

/_ Replace <USER>, <PASSWORD>, and <DATABASE> with your actual PostgreSQL user, password, and database name. _/

If you enter the interactive `psql` shell instead (for example, if you run without `-c "SELECT version();"`), you can exit at any time by typing:

```bash
\q or press `q`
```

and pressing Enter.

The expected output will look something like:

```
                                                 version
---------------------------------------------------------------------------------------------------------
 PostgreSQL 16.0 (Debian 16.0-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc, 64-bit
(1 row)
```

This confirms your Postgres server is running and responding to SQL commands inside the container.

Or you can use Docker Desktop (Windows / Mac) or Portainer (Linux)

That uses the client **inside** the container (still correct). To test **from your host** as your app would, use any `psql` client on the host:

```bash
psql "postgresql://<USER>:<PASSWORD>@localhost:5435/<DATABASE>" -c "SELECT 1;"
```

/_ Replace <USER>, <PASSWORD>, and <DATABASE> with your actual PostgreSQL user, password, and database name. _/

Sample output:

```
 ?column?
----------
        1
(1 row)
```

If you do not have `psql` installed, using `docker exec` as shown above provides a similar connection test.

---

## Step 5 — Application connection string

SQLAlchemy (with Psycopg 3) typically uses:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

With the run command above and host port **5435**, in your `.env`:

```env
DATABASE_URL=postgresql+psycopg://<USER>:<PASSWORD>@localhost:5435/<DATABASE>
```

/_ Replace <USER>, <PASSWORD>, and <DATABASE> with your actual PostgreSQL user, password, and database name. _/

Notice **`5435`**: that is the **host** side of `-p 5435:5432`.

---

### How to run the FastAPI app using this connection string

1. **Activate your virtual environment** (if you have not already):

   ```
   . .venv/bin/activate
   ```

2. **Ensure your `.env` file** contains the correct `DATABASE_URL` as shown above.

3. **Start your FastAPI app** (for example):
   ```
   fastapi dev main.py
   ```
   or, depending on your setup:
   ```
   uvicorn app.main:app --reload
   ```

This will start the FastAPI application using the database connection specified in your `.env` file.

---

## Step 6 — Stop and start later

```bash
docker stop postgres-database
docker start postgres-database
```

Logs:

```bash
docker logs -f postgres-database
```

---

## Step 7 — Remove the container (data is lost)

```bash
docker stop postgres-database
docker rm postgres-database
```

To **keep data** across removals, add a **named volume** next time:

```bash
docker run --name postgres-database \
  -e POSTGRES_USER=<USER> \
  -e POSTGRES_PASSWORD=<PASSWORD> \
  -e POSTGRES_DB=<DB_NAME> \
  -p <PORT>:5432 \
  -v fastapi_pgdata:/var/lib/postgresql/data \
  -d postgres:16
```

---

## Optional: Using `docker compose` with `.env`

The recommended filename for Docker Compose is `docker-compose.yaml` (in your project root).

### Variables (in `.env`, next to the compose file)

Docker Compose **automatically loads** a file named `.env` in the same directory as `docker-compose.yaml` and substitutes `${VAR}` in the YAML. Define at least:

| Variable                | Purpose                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| `POSTGRES_USER`         | Database role (default in compose: `postgres`)                     |
| `POSTGRES_PASSWORD`     | Password for that role (default: `password` — change for real use) |
| `POSTGRES_DB`           | Database name (default: `fastapi_crud`)                            |
| `POSTGRES_PUBLISH_PORT` | **Host** port mapped to container `5432` (default: `5435`)         |

Copy `.env.example` to `.env` and edit values. **Do not commit `.env`** if it holds secrets.

Your **FastAPI** `DATABASE_URL` must match the **same** user, password, database name, and **published host port** as in `.env`. Use a **full URL string** (Pydantic / `python-dotenv` does not expand `${VAR}` inside values the way Compose does inside YAML):

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5435/fastapi_crud
```

After you change `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, or `POSTGRES_PUBLISH_PORT`, update this line to match. If the password contains `@`, `#`, or other reserved URL characters, **URL-encode** them in `DATABASE_URL`.

You can keep **one** `.env` at the project root with both the Compose variables and `DATABASE_URL`; Compose only substitutes variables that appear in `docker-compose.yaml`, while your app reads `DATABASE_URL` as plain text.

### `docker-compose.yaml` (uses `.env` via `${…}`)

```yaml
services:
  database:
    image: postgres:16
    container_name: postgres-database
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
      POSTGRES_DB: ${POSTGRES_DB:-fastapi_crud}
    ports:
      - "${POSTGRES_PUBLISH_PORT:-5435}:5432"
    volumes:
      - fastapi_pgdata:/var/lib/postgresql/data

volumes:
  fastapi_pgdata:
```

The `:-default` syntax applies only if the variable is unset or empty; override everything in `.env` for a single source of truth.

### Commands

To start the database:

```bash
docker compose up -d
```

To run specif compose (e.g services):

```bash
docker compose up -d services
```

If you use a custom compose file name:

```bash
docker compose -f <FILE_NAME>.yaml up -d
```

If you change `POSTGRES_PUBLISH_PORT`, update `DATABASE_URL` (and any `psql` / `localhost` examples) to use that **host** port, not `5432`.

---

## Reset dev data (destructive)

Postgres **initializes users and the data directory only on first start** of a **new** volume. If you change `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` in `.env` after the volume already exists, the old cluster is unchanged—connections can fail with **role does not exist** or **password authentication failed**.

To wipe the named volume and let Postgres init again with your **current** `.env`:

1. Stop and remove containers (Compose v2):

   ```bash
   docker compose down
   ```

2. Find the exact Postgres volume name (Compose prefixes it with the **project name**, usually the folder name):

   ```bash
   docker volume ls | grep pg
   ```

   Example name: `fastapi-postgresql-crud_fastapi_pgdata` (yours may differ).

3. Remove that volume (**all data in that database is lost**):

   ```bash
   docker volume rm fastapi-postgresql-crud_fastapi_pgdata
   ```

   Use the name from step 2, not the example, if they differ.

4. Start the stack again so Postgres runs init scripts on a fresh volume:

   ```bash
   docker compose up -d
   ```

**Optional one-liner** (only if your project reliably uses that volume name—confirm with `docker volume ls` first):

```bash
docker compose down && docker volume rm fastapi-postgresql-crud_fastapi_pgdata && docker compose up -d
```

---

## Quick reference

| Where             | Port                             |
| ----------------- | -------------------------------- |
| Inside container  | `5432` (default Postgres)        |
| On your machine   | Whatever you chose (e.g. `5435`) |
| In `DATABASE_URL` | **Host** port (`5435`)           |

If connection fails, check: container is running, `-p` mapping, firewall, and that nothing else is bound to your chosen host port.
