# PaperScroll Behavior Spec

## Entry & Layout
- The app bootstraps with a blocking splash that says `Loading configuration…` until the saved reading preferences are ready.
- Once configuration loads, the user always lands on the Explore view: a single-page layout with the paper feed on the left and a hidden settings overlay that can slide in from the right.
- The global text size immediately reflects the saved `Text size` value, so reopening the app shows the interface in the reader’s preferred scale without any manual action.

## Explore View
- The header pins the `PAPERSCROLL` title and a single icon button that opens or closes Settings; clicking anywhere outside the panel also closes it.
- The feed itself is an infinite scroll list; when the reader approaches ~200 px from the bottom, the app automatically loads the next batch.
- While the app fetches additional cards, a `Loading more papers…` row sits at the end of the list.
- When no journals are configured, the list shows `Add at least one journal to start sampling papers.` so the reader knows to seed the sampler.
- Any other data-fetch problem surfaces inline above the cards with the error text that came back from the APIs.

## Paper Cards
- Each paper renders as a card with a clickable title that opens the DOI target in a new tab.
- Secondary lines surface the publication year + journal name (`2023 · Journal Title`) and the comma-separated author list.
- The abstract body text is displayed in full, allowing the user to skim without leaving the page.
- Cards are separated by thin dividers so the feed reads as a continuous scroll with clear boundaries.

## Settings Overlay
- The overlay stays hidden until summoned; once open it owns focus until the reader dismisses it via the close icon, the header toggle, or by clicking the translucent backdrop.
- Year Range: two number fields (`Start`, `End`) keep local input until Enter is pressed; values must be whole numbers between 1900 and 2100, and `End` must be ≥ `Start`. Violations surface inline errors before anything saves.
- Journals: the reader can add a journal by typing a `Name` and `ISSN` (both must be present). Invalid attempts surface `Name and ISSN are required.` inline.
- Existing journals appear as removable chips showing `Name · ISSN`; clicking the `×` badge excises that source so it is no longer considered when sampling.
- Appearance: a `Text size` number field (12–30 px) adjusts the entire app, and the `Email` field stores the contact address used for polite API requests.
- The bottom of the panel shows `Powered by OpenAlex · © Lin-Tung Tsai` as a static footer.

## Sampling Experience
- Each paper request randomly selects one of the configured journals, then picks a random year within the saved range before calling OpenAlex’s `sample=1` endpoint.
- Scrolling near the bottom repeats that process per card, so the queue stays varied without waiting for background syncs.
- If OpenAlex responds with an error (rate limit, missing data, etc.), the feed keeps going and a toast surfaces the failure detail so the reader knows to retry later.

## Notifications
- Toasts slide in at the bottom of the screen, inherit an info/error style, and auto-dismiss after roughly four seconds unless manually closed with the `×` icon.
- Only one toast is visible at a time; launching another replaces the previous message so feedback stays readable.
- On first load without an email configured, an info toast nudges the reader: `Enter email in settings to increase load speed.`

## Persistence & Offline Behavior
- All configuration fields persist locally, so returning readers keep their journal selections, email, and appearance preferences—even offline.
- The feed repopulates by sampling OpenAlex whenever connectivity allows; if the API fails, the error toast communicates the issue but the UI stays responsive.
