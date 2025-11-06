# Repository Guidelines

## Project Structure & Module Organization
- `main.py` boots the Flet app and wires navigation between Explore and Settings.
- `frontend/` contains UI modules: `ui.py` for layout primitives, `paper_display.py` for listing metadata, `settings.py` for preferences, `paper.py` for domain transforms, and `api_client.py` for HTTP calls.
- `backend/` houses the FastAPI service (`main.py`, `services.py`, `storage.py`, `schemas.py`) responsible for journal sync, config persistence, and random paper retrieval.
- `assets/` holds fonts and icons; keep additions lightweight and note license requirements.
- `storage/` stores runtime data (`storage/data/config.json`, journal caches) plus temporary files under `storage/temp`.
- `build/` contains packaged artifacts; avoid committing new build outputs without coordination.

## Build, Test, and Development Commands
- `poetry install`: provision the Python 3.13+ virtualenv with all dependencies.
- `poetry run uvicorn backend.main:app --reload`: start the API (defaults to `http://127.0.0.1:8000`; override with `PAPER_SCROLL_API_URL`).
- `poetry run flet run`: launch the desktop client; requires the backend to be running.
- `poetry run python main.py --web`: optional browser host for quick UI checks.
- `poetry run python -m pip list`: record dependency snapshots when reporting issues.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, snake_case modules/functions, and CapWords classes (e.g., `PaperDisplay`).
- Keep all network access inside `frontend/api_client.py`; UI modules should receive fully prepared data objects.
- Use f-strings for formatting and centralize shared constants in the relevant frontend or backend module to avoid duplication.

## Testing Guidelines
- No automated suite exists yet; add `tests/` with FastAPI `TestClient` coverage for endpoints and smoke tests for Explore view rendering.
- Prefer descriptive pytest names (`test_random_paper_returns_metadata`) that map to user behaviour.
- Mock Crossref/OpenAlex calls so CI/test runs stay offline; stage fixtures under `storage/temp` when necessary.

## Commit & Pull Request Guidelines
- Follow existing history: short imperative subjects (~50 chars) with optional Conventional prefixes (`feat:`, `fix:`).
- Keep related work in single commits and include context for journal sync or UI adjustments in the body when non-obvious.
- PRs should link issues, describe reproduction steps for UI changes, and attach screenshots or recordings when tweaking layouts or assets.
