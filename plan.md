# Backend/Frontend Separation Plan

## Objectives
- Decouple data fetching, persistence, and settings management from the legacy `frontend/back.py` module so the backend can run headless.
- Introduce a FastAPI service that exposes REST endpoints for papers, starring, journals config, settings, and Zotero export.
- Refactor the Flet client (or alternative UI) into a pure frontend that consumes the FastAPI API over HTTP.

## Phase 1: Discovery & Preparation
- Inventory current backend responsibilities (`frontend/api_client.py`, `frontend/settings.py`, `frontend/zotero.py`) and classify methods into domains: paper catalog, user preferences, export.
- Define JSON schemas for key payloads (`Paper`, `Journal`, `Config`, `Status`) based on existing structures in `storage/data` and Crossref responses.
- Decide on persistence: keep current `storage/` layout at first, then evaluate SQLite or lightweight document store for concurrency.

## Phase 2: FastAPI Service
- Scaffold a Poetry project under `backend/` with FastAPI, Uvicorn, and httpx (for Crossref/OpenAlex). Expose commands via `poetry run uvicorn backend.main:app --reload`.
- Split concerns into modules: `repositories/` for filesystem/DB access, `services/` for Crossref/OpenAlex orchestration, `routers/` for API endpoints, `schemas.py` for Pydantic models.
- Implement endpoints:
  - `GET /papers` (paged or infinite scroll ready); support `random`, `latest`, `journal` filters.
  - `POST /papers/{doi}/star` and `DELETE /papers/{doi}/star`.
  - `GET/PUT /config` for settings, `POST /journals:sync` to trigger re-fetch, `POST /export/zotero` for queued exports.
  - `GET /status` to surface background job progress, replacing the current `set_bk_status` callback.
- Add background tasks: Crossref syncing should run via `asyncio.create_task` or `BackgroundTasks`, writing results into storage then invalidating caches.

## Phase 3: Frontend Refactor
- Create `frontend/` directory for the Flet app; keep Poetry root or move to dedicated `frontend/pyproject.toml` if dependencies diverge.
- Replace direct `Backend` instantiation in `main.py` with an `ApiClient` layer that calls FastAPI endpoints (via `httpx` or `requests`), handling pagination, optimistic updates, and error surfaces.
- Update UI components (`paper_display.py`, `settings.py`, etc.) to consume DTOs returned by the API and manage local state separately from persistence.
- Redirect any filesystem reads/writes (e.g., starred papers) through HTTP calls to the backend service.

## Phase 4: Integration & Tooling
- Add compose file or task runner to launch both services (`poetry run uvicorn ...`, `poetry run flet run`) with shared environment variables (e.g., `API_BASE_URL`).
- Write end-to-end smoke tests using `pytest` + `httpx.AsyncClient` to validate API behavior and contract tests for frontend data models.
- Document deployment strategy: packaged backend (Docker or systemd), frontend distribution (Flet packaging) pointing to backend URL.

## Phase 5: Migration & Cleanup
- Gradually remove legacy logic from the deprecated synchronous backend module, replacing with thin proxies until full cutover.
- Migrate existing local data under `storage/` to backend-managed directories with versioned migrations.
- Update `AGENTS.md` and README with new commands, architecture diagram, and contribution expectations once refactor lands.
