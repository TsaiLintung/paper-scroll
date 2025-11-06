# Star & Zotero Decommission Plan

## Goals
- Retire all starring and Zotero-export functionality from both backend and frontend.
- Simplify the data model, storage layout, and contributor workflow so no optional credentials are required.
- Ensure remaining features (paper discovery, journal sync, settings) continue to work without regressions.

## Phase 1 – Discovery & Design
- Catalogue affected modules: backend (`services.py`, `storage.py`, `main.py`, `schemas.py`, `config.py`), frontend (`main.py`, `paper_display.py`, `api_client.py`, `settings.py`, `zotero.py`), documentation (`README.md`, `AGENTS.md`), and `storage/starred`.
- Decide what replaces the dedicated “Starred” view—either remove the tab entirely or repurpose it (e.g., “Recently Fetched”).
- Define the slimmed-down config schema; drop `zotero_id`, `zotero_key`, and any star-specific flags, and plan a migration step to rewrite `config.json`.

## Phase 2 – Backend Cleanup
- Remove star-specific storage helpers (`FileStorage.star_paper`, `unstar_paper`, etc.) and delete the `starred` directory if empty.
- Delete FastAPI routes related to starring and Zotero export; adjust `schemas.py` and `BackendService` accordingly.
- Strip Zotero configuration fields from `DEFAULT_CONFIG`, config payloads, and validation; provide a one-time migration to purge orphaned keys from existing `config.json`.
- Update unit or integration tests (if any) to reflect the smaller API surface; add a smoke test for the remaining endpoints.

## Phase 3 – Frontend Simplification
- Remove the “Starred” navigation destination and `StaredPapers` view from `main.py`; collapse routing logic to two tabs (Explore, Settings).
- Prune star/Zotero controls from `PaperDisplay`, eliminating toggle state, extra buttons, and optimistic update handling.
- Delete `frontend/zotero.py` and related API client methods; simplify `ApiClient` to only expose configuration, journal sync, and random paper endpoints.
- Refresh Settings UI to omit Zotero credential fields; ensure status messaging still works when the backend is offline.

## Phase 4 – Data & Docs
- Provide a cleanup script or instructions for users to delete residual `storage/data/starred` JSON files.
- Update `README.md`, `AGENTS.md`, and any onboarding docs to reflect the leaner feature set and command list.
- Double-check packaging/build artefacts (`build/`) to ensure no stale assets reference star/Zotero icons.

## Phase 5 – Validation & Follow-up
- Manually test: journal sync path, exploring papers (including empty states), settings edits, and backend offline behaviour.
- Tag backlog items for future enhancements (e.g., replace starring with external bookmarking, add share/export options).
- Communicate the removal in release notes, highlighting that existing starred data and Zotero integration are deprecated.
