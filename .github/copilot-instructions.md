## Quick orientation for AI coding agents

This repository is a small microservices workshop (FastAPI + Flask) scaffolded for students. The guidance below highlights the concrete, discoverable patterns and files an agent should use to be productive here.

1) Big picture
- Frontend: `frontend/app.py` (Flask) — talks to the API Gateway via the env var `API_GATEWAY_URL`.
- API Gateway: `api-gateway/main.py` (FastAPI) — routes client requests to internal services using the `SERVICES` lookup and `requests`.
- Microservices: `services/*/main.py` (FastAPI) — each service exposes a `/health` endpoint and TODO skeletons for real endpoints.
- Datastores: example DB modules live under `services/<name>/database_*.py` (Postgres/SQLAlchemy, Redis, Mongo templates are present in the scaffold).
- Orchestration: `docker-compose.yml` defines container names, ports, and DATABASE_URL/other envs used by code.

2) Concrete developer workflows (how to run / debug)
- Local dev / full stack: copy `.env.example` -> `.env`, then run:

  docker-compose up --build

  This builds images and uses container names/ports referenced in the code (e.g. `api-gateway:8000`, `auth-service:8001`, `service1-service:8002`).
- Individual services: run the FastAPI app directly (they are standard FastAPI apps) e.g. `uvicorn services/service1.main:app --reload --port 8002`.
- Database debug: services expect a `DATABASE_URL` env var (see `services/service1/database_sql.py`) — set it to the container DB URL or a local DB for debugging.

3) Project-specific conventions and patterns
- Service naming / docker-compose sync: the gateway uses service hostnames that must match the docker-compose service names. If you change a service name in `docker-compose.yml`, update `api-gateway/main.py` (the `SERVICES` map) or prefer environment variables (the code reads env vars by default).
- Health checks: every service template implements `GET /health` — use these for quick liveness checks.
- Gateway forwarding: `api-gateway/main.py` implements generic `GET`/`POST` forwarding using `requests`. When adding new services, add the mapping to `SERVICES` and ensure the target service path exists.
- DB pattern: SQL services use SQLAlchemy with a `DATABASE_URL` env var and a `create_db_and_tables()` helper. Look at `services/service1/database_sql.py` for the exact pattern (engine, SessionLocal, get_db dependency).

4) Integration points and external dependencies
- Inter-service HTTP: services communicate via HTTP through the API Gateway (or directly using container hostnames when needed). See gateway `forward_get`/`forward_post` for examples.
- Databases: the scaffold expects different DB engines per service (Mongo for auth in the compose example, Postgres for `service1`). Update `DATABASE_URL` in `docker-compose.yml` when wiring a real DB.
- Environment variables: `common/config.py` loads `.env` and provides `settings.API_GATEWAY_URL` as a single-source reference for scripts/utilities.

5) What to change when adding a new service (minimal checklist)
- Add service folder under `services/` with `main.py`, `Dockerfile`, `requirements.txt`.
- Implement `GET /health` and your API endpoints (prefer `/api/v1` prefix if including via router).
- Add DB module if needed following `services/service1/database_sql.py` pattern and set `DATABASE_URL`.
- Add service and DB entries to `docker-compose.yml` (container name must match the host used by `api-gateway`), then run `docker-compose up --build`.
- Update `api-gateway/main.py` SERVICES map or set an env var to expose the new service to the gateway.

6) Examples (copy-paste friendly)
- Frontend -> gateway request (pattern used in `frontend/app.py`):

  requests.get(f"{API_GATEWAY_URL}/api/v1/<service_name>/<path>")

- Gateway entry example (`api-gateway/main.py`): add service to SERVICES:

  SERVICES = {"auth": "http://auth-service:8001", "myservice": "http://service1-service:8002"}

- SQLAlchemy DB pattern (`services/service1/database_sql.py`): engine from `DATABASE_URL`, `SessionLocal`, `get_db()` generator, and `create_db_and_tables()`.

7) Files to inspect first when making changes
- `docker-compose.yml` (service names, ports, envs)
- `api-gateway/main.py` (routing and service discovery)
- `frontend/app.py` (how the UI calls the gateway)
- `common/config.py` (env loading and settings)
- `services/<name>/main.py`, `models.py`, `database_*.py`, `Dockerfile`, `requirements.txt` for service-specific patterns

8) Notes for AI agents
- Prefer small, local edits that match existing TODOs and code style (these files are intentionally template-like). Don't rename services without updating `docker-compose.yml` and the gateway's `SERVICES` mapping.
- Use concrete examples from above when changing code so humans can validate quickly (e.g., add a `/health` route, update `SERVICES` mapping, or add `DATABASE_URL` to compose).
- The repo uses FastAPI + Flask and plain `requests` for HTTP; avoid introducing heavy new frameworks unless needed.

If anything here is unclear or you'd like deeper examples (e.g., a worked example of adding a Postgres-backed endpoint and the compose entries), tell me which service to extend and I will add a focused how-to.
