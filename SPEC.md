# PaperScroll Behavior Spec

## Entry & Layout
- The app bootstraps with a blocking splash that says `Loading configuration…` until the saved reading preferences are ready.
- Once configuration loads, the user always lands on the Explore view: a single-page layout with the paper feed on the left and a hidden settings overlay that can slide in from the right.
- The global text size immediately reflects the saved `Text size` value, so reopening the app shows the interface in the reader’s preferred scale without any manual action.

## Explore View
- The header pins the `PAPERSCROLL` title and two icon buttons: one to refresh the feed and one to open or close Settings.
- The refresh control re-randomizes the queue from the cached journal snapshots and replaces the entire list at once.
- The settings control toggles the overlay; clicking anywhere outside the panel also closes it.
- The feed itself is an infinite scroll list; when the reader approaches ~200 px from the bottom, the app automatically loads the next batch.
- While the app fetches additional cards, a `Loading more papers…` row sits at the end of the list.
- When the feed runs without synced journals, the list shows `No journal data yet. Run “Update journals” to fetch metadata.` so the user knows to trigger a sync.
- Any other data-fetch problem surfaces inline above the cards with the error text that came back from the APIs.

## Paper Cards
- Each paper renders as a card with a clickable title that opens the DOI target in a new tab.
- Secondary lines surface the publication year + journal name (`2023 · Journal Title`) and the comma-separated author list.
- The abstract body text is displayed in full, allowing the user to skim without leaving the page.
- Cards are separated by thin dividers so the feed reads as a continuous scroll with clear boundaries.

## Settings Overlay
- The overlay stays hidden until summoned; once open it owns focus until the reader dismisses it via the close icon, the header toggle, or by clicking the translucent backdrop.
- Year Range: two number fields (`Start`, `End`) update immediately; changing either silently re-syncs journals because it affects what should be cached.
- Journals: the reader can add a journal by typing a `Name` and `ISSN` (both must be present). Invalid attempts surface `Name and ISSN are required.` inline.
- Existing journals appear as removable chips showing `Name · ISSN`; clicking the `×` badge excises that source and silently re-runs sync in the background.
- Appearance: a `Text size` number field (12–30 px) adjusts the entire app, and the `Email` field stores the contact address used for polite API requests.
- Journal Sync: a primary button triggers `Update journals`; while the worker is busy, the button label switches to `Updating…` and stays disabled.
- The sync section also shows the latest status message (e.g., `Fetching AER (2021)` or `All journals updated.`) plus a determinate progress bar driven by worker updates.

## Sync Experience
- A manual sync always ends with a toast: `Journals updated.` on success or the error detail if something failed.
- The very first visit automatically launches a silent sync when no journal snapshots exist yet, so the feed populates without extra clicks.
- Adjusting `Start year`, `End year`, `Email`, or the journal list triggers a background sync without spamming toasts; the reader just sees the status and progress update.
- When the sync worker encounters an error mid-run, the status text reflects the failure and the toast shows the same message so the user knows follow-up is required.

## Notifications
- Toasts slide in at the bottom of the screen, inherit an info/error style, and auto-dismiss after roughly four seconds unless manually closed with the `×` icon.
- Only one toast is visible at a time; launching another replaces the previous message so feedback stays readable.

## Persistence & Offline Behavior
- All configuration fields, journal snapshots, sync statuses, and fetched paper details persist locally, so returning readers pick up exactly where they left off—even offline.
- Cached papers load immediately from storage; when the device regains connectivity, the app can still refresh individual cards as the reader scrolls deeper into the queue.
