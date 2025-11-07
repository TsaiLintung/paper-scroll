# Repository Guidelines

## Project Structure & Module Organization
- `src/` hosts all TypeScript sources. UI lives under `src/components`, React hooks in `src/hooks`, business/data layers in `src/domain`, `src/services`, and `src/data`, while shared types sit in `src/types`.
- Global styles live in `src/App.css` plus per-component CSS modules; assets such as icons are under `src/assets`.
- Tests stay co-located with their targets (e.g., `src/domain/paper.test.ts`). Keep new specs beside the code they cover.

## Build, Test, and Development Commands
- `npm run dev` — start Vite with Fast Refresh at `http://localhost:5173`.
- `npm run build` — run TypeScript project references then emit the production bundle into `dist/`.
- `npm run preview` — serve the latest `dist/` output (production sanity check).
- `npm run lint` — execute ESLint using `eslint.config.js`; fix or suppress violations before opening a PR.
- `npm test` / `npm test -- --run` — run Vitest suites (watch vs. single pass).

## Coding Style & Naming Conventions
- TypeScript everywhere with two-space indentation and single quotes for strings.
- React components use PascalCase (`ExploreView`, `SettingsPanel`); hooks use `useX` naming.
- Favor small, focused components; keep domain logic in `src/domain`/`src/services` and treat UI layers as thin presenters.
- Run ESLint and rely on TypeScript to surface unused symbols before committing.

## Testing Guidelines
- Vitest drives unit testing. Mirror the `*.test.ts` naming and colocate specs with the code under test.
- Mock browser APIs (IndexedDB, fetch) with lightweight fakes—never perform real network calls.
- Write behavior-focused assertions (state transitions, rendered DOM) and add regression tests alongside any bug fix.

## Commit & Pull Request Guidelines
- Follow the repo’s history: short, action-oriented commit messages ≤72 chars (e.g., `add settings reset button`).
- Each PR should provide: summary of changes, screenshots for UI updates, linked issue/story, and a checklist covering `npm test`, `npm run lint`, and `npm run build` results.
- Squash noisy fixups locally and keep each PR focused on one logical change.

## Configuration Tips
- OpenAlex base URL is configurable through `VITE_OPENALEX_BASE`; defaults to `https://api.openalex.org`.
- User preferences persist in `localStorage`. Use the built-in “Reset preferences” button (Settings footer) to return to `DEFAULT_CONFIG` when testing.*** End Patch` to=functions.apply_patch  Nsjson
