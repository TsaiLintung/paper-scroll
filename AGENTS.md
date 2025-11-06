# Repository Guidelines

## Project Structure & Module Organization
- `main.py` boots the Flet app and connects it to the HTTP client.
- `frontend/` houses UI modules: `ui.py` for layout primitives, `paper_display.py` for list rendering, `settings.py` for preferences, `paper.py` for domain transforms, and `api_client.py` for backend calls.
- `backend/` exposes the FastAPI service (`main.py`, `services.py`, `storage.py`, `schemas.py`) that handles Crossref/OpenAlex sync, persistence, starring, and Zotero exports.
- `assets/` contains bundled fonts and app icons; keep new assets lightweight and document licensing.
- `storage/` carries runtime caches (`storage/data`) and transient files (`storage/temp`). Anything generated at runtime should live here so builds stay clean.
- `build/` stores platform artifacts created by Flet packaging; avoid checking in additional build outputs.

## Build, Test, and Development Commands
- `poetry install`: set up the Python 3.13+ environment with runtime deps.
- `poetry run uvicorn backend.main:app --reload`: start the FastAPI backend (default `PAPER_SCROLL_API_URL` is `http://127.0.0.1:8000`).
- `poetry run flet run`: launch the desktop client; ensure the backend is running first.
- `poetry run python main.py --web`: optional browser host; set `PAPER_SCROLL_API_URL` for remote backends.
- `poetry run python -m pip list`: confirm dependency versions before filing issues or reproducing bugs.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, snake_case for functions/modules, and CapWords for classes such as `PaperDisplay`.
- Favor explicit imports within `frontend` modules and keep API access funneled through `ApiClient`.
- Use f-strings for formatting, and centralize configuration constants in `frontend/settings.py` or backend service modules to avoid magic values.

## Testing Guidelines
- No automated suite exists yet; when adding coverage, create `tests/` with backend API tests (FastAPI `TestClient`) and frontend smoke checks.
- Prefer `pytest` with descriptive test names (`test_refresh_button_scrolls_to_top`) matching user-facing behavior.
- Stub Crossref/OpenAlex traffic in backend tests (e.g., `responses` or `httpx_mock`) so runs stay offline; store sample fixtures under `storage/temp` if needed.

## Commit & Pull Request Guidelines
- Follow the existing Git history: short imperative subjects (~50 chars), optional Conventional prefix (`fix:`, `feat:`) when appropriate.
- Keep related changes in a single commit and include context on data sources or UI tweaks in the body when non-obvious.
- PRs should link relevant issues, include reproduction steps for UI changes, and attach screenshots or screen recordings when altering layouts or assets.
