# Repository Guidelines

This React + TypeScript + Vite workspace centers on a layered structure that keeps UI, domain logic, and browser integrations separate. Use the following reference when building, testing, or reviewing contributions.

## Project Structure & Module Organization
- `src/components` holds presentational React components; prefer small, focused trees under feature folders.
- `src/domain`, `src/services`, and `src/workers` encapsulate business rules, data access, and long-running browser tasks—treat these as the single sources of truth.
- `src/hooks`, `src/theme`, and `src/assets` supply reusable behavior, design tokens, and static media.
- `src/data` hosts seed/config files, while `src/types` centralizes shared interfaces. Keep tests near the code they cover (e.g., `src/domain/paper.test.ts`).

## Build, Test, and Development Commands
- `npm run dev` — launch the Vite dev server with Fast Refresh.
- `npm run build` — type-check with `tsc -b` before emitting an optimized production bundle.
- `npm run preview` — serve the latest build locally to verify production artifacts.
- `npm run lint` — run ESLint (`eslint.config.js`) across the repo; fix findings before submitting.
- `npm test` — execute Vitest suites in watchable mode; use `npm test -- --run` for CI-like runs.

## Coding Style & Naming Conventions
- TypeScript everywhere; favor explicit types in boundary layers (`services`, `domain`).
- Two-space indentation, single quotes for strings, and React function components named `PascalCase`.
- Co-locate styles in `*.css` modules or `App.css`; avoid inline styles for reusable components.
- Run ESLint and let TypeScript surface unused symbols before pushing.

## Testing Guidelines
- Vitest drives all automated tests; extend `src/domain/*.test.ts`-style colocated files for new modules.
- Mock IndexedDB and fetch calls via lightweight fakes; avoid network access in tests.
- Assert observable behavior (state transitions, DOM output) instead of implementation details; add regression specs when fixing bugs.

## Commit & Pull Request Guidelines
- Follow the existing log style: short, action-oriented sentences (e.g., `fully switch to web version`); keep to ≤72 chars and focus on the “what”.
- Each PR should include: summary, screenshots or recordings for UI changes, linked issue/shortcut, test plan (`npm test`, `npm run lint`, build) in checklist form.
- Squash noisy fixup commits locally; reviewers expect one logical change per PR.
