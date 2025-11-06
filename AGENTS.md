# Repository Guidelines

## Project Structure & Module Organization
`main.py` boots the Flet client and drives navigation between Explore and Settings. Frontend modules live in `frontend/`, with `ui.py` for layout primitives, `paper_display.py` for metadata lists, `settings.py` for preferences, `paper.py` for domain transforms, and `api_client.py` handling HTTP calls. The FastAPI backend sits in `backend/` (`main.py`, `services.py`, `storage.py`, `schemas.py`) and covers journal sync, config persistence, and random paper retrieval. Runtime data lands under `storage/`, static assets stay in `assets/`, and packaged artifacts are kept in `build/`. Use `storage/temp` for disposable fixtures or download caches.

## Build, Test, and Development Commands
- `poetry install` — bootstrap the Python 3.13+ virtualenv with project dependencies.
- `poetry run uvicorn backend.main:app --reload` — launch the API locally at `http://127.0.0.1:8000`.
- `poetry run flet run` — start the desktop client (requires the API to be running first).
- `poetry run python main.py --web` — host the Flet UI in a browser for quick smoke checks.
- `poetry run python -m pip list` — capture dependency snapshots when filing issues or PRs.

## Coding Style & Naming Conventions
Stick to PEP 8 with 4-space indentation. Use CapWords for classes (e.g., `PaperDisplay`) and snake_case for modules, functions, and variables. Prefer f-strings for formatting, and centralize shared constants within the relevant frontend or backend module to avoid duplication. Keep UI modules free from raw network calls—route all HTTP traffic through `frontend/api_client.py`.

## Testing Guidelines
Pytest is the assumed framework. Add FastAPI `TestClient` coverage for backend endpoints and smoke tests for the Explore view when introducing features. Use descriptive names such as `test_random_paper_returns_metadata`, and stage any fixtures or cached API payloads under `storage/temp`. Mock third-party services (Crossref, OpenAlex) so the suite stays offline-friendly.

## Commit & Pull Request Guidelines
Follow the existing history: concise imperative subjects (~50 chars) with optional prefixes like `feat:` or `fix:`. Group related work in single commits, and document rationale for backend sync or UI layout changes in the body when not obvious. PRs should link issues, include reproduction steps, and attach screenshots or recordings for visual changes. Note licensing when introducing new assets inside `assets/`.

## Security & Configuration Tips
Expose the API URL via the `PAPER_SCROLL_API_URL` environment variable when deploying or testing against alternate backends. Keep `storage/data/config.json` out of version control tweaks unless changes are intentional. Treat `storage/temp` as disposable and purge sensitive downloads before committing.
