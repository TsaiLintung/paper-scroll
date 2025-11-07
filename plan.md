# Plan: Replace Crossref Snapshot Indexing with OpenAlex Sampling

## Goals
- Remove the Crossref-driven journal snapshot workflow (worker, IndexedDB snapshots, sync UI semantics).
- Load papers on-demand by sampling OpenAlex works for a randomly chosen journal + year within the configured range.
- Keep the Settings panel controls but reinterpret “Update journals” (or rename later) so it no longer depends on snapshots.

## Proposed Steps

1. **Define the new sampling source of truth**
   - Decide how we store selected journals and year ranges (likely the existing `config` suffices).
   - Document how we pick a `(journal, year)` pair per fetch (e.g., shuffle journals, random year between `start_year`/`end_year`).
   - Clarify how many sample attempts we make before surfacing an error toast.

2. **Introduce an OpenAlex sampling helper**
   - Extend `src/services/openalex.ts` with a method like `sampleWorks({ issn, year, sampleSize, email })`.
   - Read OpenAlex’s `sample=` query parameter docs and ensure we’re hitting `/works` with filters for ISSN/year plus `sample`.
   - Keep the existing rate limiter so we still respect 10 req/s.

3. **Rework feed loading logic**
   - Rewrite `usePaperFeed` to drop DOI pools from snapshots; instead, for each needed paper:
     1. Randomly choose a journal & year.
     2. Call the new OpenAlex sampling endpoint to grab 1 work.
     3. Convert to `PaperViewModel` and push into the feed.
   - Handle errors per attempt and surface them via the existing toast callback without inserting placeholder cards.

4. **Remove Crossref + snapshot infrastructure**
   - Delete `src/services/crossref.ts`, the sync worker (`src/workers/syncWorker.ts`), and `src/services/sync.ts`.
   - Drop snapshot-related data-store APIs (`saveSnapshot`, `getSnapshots`, etc.) and schema stores from IndexedDB (`journalSnapshots`, `status` if unused).
   - Remove `useSyncService`, `useStatus`, and the Settings “Update journals” button behavior (or repurpose it if we still want a manual refresh trigger).

5. **Simplify UI/UX around syncing**
   - Update `SettingsPanel` copy to reflect the new behavior (maybe rename “Update journals” to “Refresh feed cache” or remove the button if unnecessary).
   - Ensure the Explore view still supports refresh/infinite scroll using the new sampling logic.
   - Adjust toasts/status messaging now that sync status/progress are gone.

6. **Clean up types/tests**
   - Remove `JournalSnapshot` types, sync worker message types, and associated Vitest files.
   - Add/update tests for `toPaperViewModel` (if needed) and any new helper that selects journals/years.

7. **Data migration & backward compatibility**
   - Decide how to handle existing IndexedDB stores that include `journalSnapshots` and `status`; either bump DB version and delete old stores or keep reading but ignore.
   - Verify cold-start logic now simply triggers a feed refresh rather than a “sync”.

8. **Validation**
   - Update docs/README to describe the new OpenAlex-only workflow.
   - Run `npm run lint`, `npm test -- --run`, and `npm run build` before shipping.

## Open Questions / Follow-ups
- Do we still need the “Update journals” CTA once snapshots vanish, or should we replace it with a “Warm up cache” action? -> Drop the button.
- How many sample retries should we attempt per batch before giving up? -> 10.
- Should we add pagination or caching for sampled works to avoid duplicates across refreshes? -> No need.
