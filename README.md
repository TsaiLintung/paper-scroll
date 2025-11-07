## PaperScroll

PaperScroll is a lightweight reading companion for researchers who track long lists of academic journals. It samples works directly from OpenAlex (using the `sample` query) based on the reader’s journal list and year range, then renders the queue in a clean, scrollable layout. Preferences live entirely in the browser (IndexedDB), so returning to the app restores the exact reading setup without additional sync steps.

### Features
- **Infinite paper feed** — scroll through randomly sampled works while the app prefetches more as you near the bottom; no manual refresh button needed.
- **On-demand OpenAlex sampling** — each card picks a random journal-year combo within the configured range, then calls `sample=1` to fetch a work.
- **Configurable reading experience** — adjust text size, year ranges (commit with Enter, validated between 1900–2100), contact email, and journal lists inside the settings overlay.
- **Local-first storage** — configs live in IndexedDB via `idb`, so reopening the app keeps your preferences intact even offline.
- **Gentle nudges** — if no email is set, the app shows a toast reminding readers that providing one speeds up polite OpenAlex access.

### Tech Stack
- React 19 + TypeScript, styled with modular CSS files (`src/App.css`, `src/components/*.css`).
- Vite 7 for dev server, bundling, and environment variable injection.
- Vitest for unit tests (see `src/domain/paper.test.ts` for the current pattern).
- OpenAlex API with an optional base override via `VITE_OPENALEX_BASE`.

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
- Journal, year, and email settings persist via `src/data/db.ts` (default includes AER, ISSN 0002-8282).
- Year inputs accept whole numbers between 1900 and 2100, require `End ≥ Start`, and only save when you press Enter—useful for experimenting before committing changes.
- API hosts fall back to public OpenAlex; create `.env.local` with `VITE_OPENALEX_BASE` to point at mirrors or proxies.

### Project Layout
- `src/components` — UI primitives such as `ExploreView`, `PaperCard`, `SettingsPanel`, and `Toast`.
- `src/hooks` — orchestration hooks (`useConfig`, `usePaperFeed`) that glue UI to the data layer.
- `src/data` — IndexedDB helpers plus `DataStore`, which manages reader configuration.
- `src/services` — API clients for OpenAlex (sampling, etc.).
- `src/domain`, `src/types` — domain-specific models, adapters, and utilities. Align new behavior with these folders to keep presentation thin.

### GitHub Pages Deployment
- The Vite `base` defaults to relative asset URLs (so it works on both custom domains and the `https://<user>.github.io/paper-scroll/` path). Set `VITE_PUBLIC_BASE` if you need to pin a different prefix.
- A workflow (`.github/workflows/deploy.yml`) builds on every push to `main`, uploads `dist/`, and publishes it via `actions/deploy-pages`.
- Enable GitHub Pages for the repo (Settings → Pages → Source: “GitHub Actions”) the first time you run the workflow.
- For manual redeploys, trigger the workflow from the Actions tab or push a new commit to `main`.

Need contribution details? Read `AGENTS.md` for coding conventions, testing expectations, and pull-request requirements.
