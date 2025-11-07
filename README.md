## PaperScroll

PaperScroll is a lightweight reading companion for researchers who track long lists of academic journals. It fetches recent DOIs from Crossref, enriches them with OpenAlex metadata, and stores everything in the browser (IndexedDB) so the feed stays fast and offline-friendly. Use it to keep a rolling queue of papers to skim, tweak journal cohorts, and monitor sync progress without leaving the page.

### Features
- **Infinite paper feed** — scroll through cached works, pull-to-refresh, and load more without reloading.
- **Journal sync worker** — a dedicated web worker queries Crossref per journal-year slice to avoid blocking the UI.
- **Configurable reading experience** — adjust text size, year ranges, contact email, and journal lists inside the settings overlay.
- **Local-first storage** — configs, sync snapshots, status updates, and cached papers live in IndexedDB via `idb`, so returning to the app resumes instantly.

### Tech Stack
- React 19 + TypeScript, styled with modular CSS files (`src/App.css`, `src/components/*.css`).
- Vite 7 for dev server, bundling, and environment variable injection.
- Vitest for unit tests (see `src/domain/paper.test.ts` for the current pattern).
- Crossref & OpenAlex APIs with optional overrides through `VITE_CROSSREF_BASE` and `VITE_OPENALEX_BASE`.

### Getting Started
```bash
npm install
npm run dev        # start Vite dev server with HMR
npm run lint       # eslint . using eslint.config.js
npm test           # vitest in watch mode
npm run build      # type-check + production bundle in dist/
npm run preview    # serve the latest build locally
```

### Configuration
- Journal, year, and email settings live under `src/data/db.ts` and persist to IndexedDB (default includes AER, ISSN 0002-8282).
- API hosts fall back to public endpoints; create `.env.local` with `VITE_CROSSREF_BASE` or `VITE_OPENALEX_BASE` to point at mirrors or proxies.
- Long-running sync work happens inside `src/workers/syncWorker.ts`, orchestrated by `SyncService`. Ensure browsers support module workers.

### Project Layout
- `src/components` — UI primitives such as `ExploreView`, `PaperCard`, `SettingsPanel`, and `Toast`.
- `src/hooks` — orchestration hooks (`useConfig`, `usePaperFeed`, `useSyncService`, etc.) that glue UI to the data layer.
- `src/data` — IndexedDB helpers plus `DataStore`, which manages configs, snapshots, and cached papers.
- `src/services` — API clients for Crossref/OpenAlex and the sync orchestration logic.
- `src/domain`, `src/types` — domain-specific models, adapters, and utilities. Align new behavior with these folders to keep presentation thin.

### GitHub Pages Deployment
- The Vite `base` is set to `/paper-scroll/`, so static assets resolve correctly when served from `https://<user>.github.io/paper-scroll/`.
- A workflow (`.github/workflows/deploy.yml`) builds on every push to `main`, uploads `dist/`, and publishes it via `actions/deploy-pages`.
- Enable GitHub Pages for the repo (Settings → Pages → Source: “GitHub Actions”) the first time you run the workflow.
- For manual redeploys, trigger the workflow from the Actions tab or push a new commit to `main`.

Need contribution details? Read `AGENTS.md` for coding conventions, testing expectations, and pull-request requirements.
