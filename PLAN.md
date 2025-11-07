# Static Website Migration Plan

## Overview
Paper Scroll surfaces random research papers from Crossref journals and enriches them with OpenAlex metadata so readers can browse abstracts, authors, and journal details through an infinite scroll UI with configurable preferences. The new target is a fully static Progressive Web App that runs entirely in the browser, syncing journal indexes on demand and caching results locally for offline-friendly reading sessions.

**Tech stack**
- Build tooling: Vite + React + TypeScript for component-driven UI and type-safe domain logic.
- Styling: CSS variables with Tailwind for theme tokens matching the current Flet design.
- Data layer: IndexedDB via the `idb` helper library, plus Web Workers for journal sync/background buffering.
- Networking: Native `fetch` with modular clients for Crossref and OpenAlex, using AbortController + retry helpers.
- Testing & quality: ESLint, Prettier, Vitest for units, and Playwright for smoke tests before deployment.

## Step-by-step plan
1. **Baseline audit and requirements capture**
   - Inventory the current Flet UI flows (`ExploreView`, `Settings`) and FastAPI endpoints (`/config`, `/journals`, `/status`, `/papers/random`) to map inputs/outputs.
   - Document config schema (start/end year, text size, email, journals) and journal snapshot format so the JS version can keep the same data contracts.

2. **Decide on the static stack and scaffold the project**
   - Pick a modern JS toolchain (e.g., Vite + React + TypeScript) that can compile to a static bundle served from any CDN.
   - Mirror the existing module boundaries: `src/ui`, `src/features/explore`, `src/features/settings`, `src/data`.
   - Add linting/formatting (ESLint, Prettier) and testing (Vitest/Playwright) to replace the current Python tooling.

3. **Model data contracts in TypeScript**
   - Define interfaces for `Config`, `Journal`, `Status`, `Paper`, and `JournalSnapshot` based on the Python models.
   - Port the `Paper` domain transform (authors list, abstract reconstruction, formatted metadata) into a reusable JS utility.
   - Establish shared constants (default config, theme tokens) that mimic `frontend/ui.py` and `backend/config.py`.

4. **Introduce an IndexedDB persistence layer**
   - Implement a thin wrapper around `indexedDB` (or use `idb`) that exposes stores for `config`, `journalSnapshots`, and cached `papers`.
   - Provide migration scripts to seed defaults on first load and to clear/upgrade stores safely.
   - Replace `storage/data/config.json` and `storage/journals/*.json` with IndexedDB reads/writes handled through a `DataStore` service.

5. **Replace the backend services with browser-side data fetchers**
   - Create `crossrefClient` and `openAlexClient` modules that use `fetch` with retry/backoff, mirroring `BackendService._fetch_crossref_journal_year` and `_load_random_paper`.
   - Move journal sync logic into a Web Worker (or background task) so large downloads don’t block the UI; stream progress updates back via `postMessage`.
   - Persist fetched journal-year snapshots directly into IndexedDB; maintain a `status` record for progress messages previously supplied by `/status`.

6. **Implement a client-side paper buffer and selection logic**
   - Recreate the Python buffer (`BUFFER_SIZE = 10`) in JS to prefetch OpenAlex metadata and emit normalized `Paper` objects to the UI.
   - Ensure the worker populates the buffer from the IndexedDB journal index, falling back to the default DOI when necessary.
   - Expose a hook/service (e.g., `useRandomPaperFeed`) that powers infinite scroll and refresh events.

7. **Rebuild the UI in JS**
   - Port the Explore view: stack layout, infinite scroll triggers, refresh button, `PaperDisplay` card styling, and settings overlay toggle.
   - Port the Settings view: year range inputs, text size/email fields, journal add/remove controls, update (sync) button, and status message/progress bar.
   - Centralize theme tokens and spacing constants so cards look consistent with the Flet version; use CSS variables for typography scaling.

8. **Wire the UI to the new data layer**
   - Replace `ApiClient` calls with hooks/services that read/write IndexedDB and trigger sync workers.
   - Keep optimistic UI updates (e.g., updating the journal chip list immediately) and surface errors via toasts/snackbars similar to the Flet notifications.
   - Ensure settings changes (text size) propagate to the theme context so Explore updates live, matching current behavior.

9. **Testing, hardening, and deployment**
   - Add unit tests for data transformers, IndexedDB helpers, and fetch clients; add integration tests that mock Crossref/OpenAlex to verify sync + feed.
   - Provide a smoke-test script that runs `npm run build && npm run preview` to mimic `poetry run python main.py --web`.
   - Configure static hosting (e.g., GitHub Pages, Netlify) and document environment variables or rate-limit considerations; remove unused Python tooling once parity is confirmed.

## Immediate next steps
- Implement real Crossref/OpenAlex fetch clients plus a Web Worker that replicates the Python backend sync flow while persisting journal snapshots to IndexedDB.
- Replace the seed-based `usePaperFeed` hook with buffer management that reads IndexedDB snapshots, selects DOIs, pulls OpenAlex metadata, and caches paper records locally.
- Enhance UI wiring so the Explore feed listens for worker progress events, updates the status overlay live, and surfaces toast/snackbar errors for sync failures.
- Expand Vitest coverage to the new IndexedDB helpers, hooks, and sync service; add component tests for the Settings and Explore views once data is live.

## Feature parity checklist
- Infinite scroll Explore view that continuously loads random papers, adds dividers between cards, and shows a fallback message when no papers are available.
- `PaperDisplay` cards showing clickable titles (DOI links), formatted abstract text, year + journal metadata, and comma-separated author lists.
- Refresh button that clears the current feed, refills the buffer, and scrolls to the top.
- Modal/overlay Settings panel with toggle button, mirroring the desktop layout and spacing.
- Config management: edit start/end years with validation, text size slider/input, and optional email field that feeds OpenAlex requests.
- Journal management: add journal form with validation, duplicate detection, removable chips, and persistence.
- “Update journals” action that launches a background sync, exposes message + progress bar, and refreshes the local config when complete.
- Backend status/error messaging replicated via snackbars/toasts and inline status text when network requests fail.
- Local persistence of config, journal snapshots, and cached papers so the experience survives reloads/offline sessions via IndexedDB.
- Theme and typography scaling driven by the stored `text_size`, preserving the look/feel defined in `frontend/ui.py`.
