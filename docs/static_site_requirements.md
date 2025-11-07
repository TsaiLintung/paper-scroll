# Static Site Requirements

## Use cases & flows
- **Explore feed** – infinite scroll of enriched paper cards, divider between entries, manual refresh button resets the buffer and scroll position.
- **Settings overlay** – modal panel with year range inputs, journal add/remove controls, update/sync button showing progress text + bar, and general preferences (text size, email).
- **Backend status messaging** – snackbars + inline progress text when sync or fetch fails; backend availability toggles settings banner.

## Data contracts
- **Config**
  - `start_year`, `end_year`: integers (YYYY) delimiting journal snapshots to sync.
  - `text_size`: integer driving typography scale across the UI.
  - `email`: optional string appended to OpenAlex `mailto`.
  - `journals`: list of `{ name: string, issn: string }`, kept unique on both fields.
- **Journal snapshot**
  - Stored per journal/year; JSON payload with `issn`, `name`, `year`, and `items` list of `{ DOI }`.
- **Paper metadata**
  - Derived from OpenAlex response; normalized fields used by UI: `display_name`, `doi` (URL), `abstract_inverted_index`, `publication_year`, `primary_location.source.display_name`, `authorships`.
  - Derived view-model adds `abstract`, `year_journal`, `authors_joined`, `valid`.
- **Status payload**
  - Tuple/message pair representing progress text + float progress, previously sourced from `/status`.

## API endpoints to replicate client-side
| Endpoint | Purpose | Replacement |
|----------|---------|-------------|
| `GET /config` | Load persisted config defaults | Read config store from IndexedDB |
| `PATCH /config` | Update single config fields | Write field to IndexedDB + emit change event |
| `POST /journals` | Add journal entry | Validate uniqueness, append in IndexedDB |
| `DELETE /journals/{issn}` | Remove journal | Delete entry in IndexedDB |
| `POST /journals/sync` | Trigger Crossref fetch | Run sync logic inside Web Worker |
| `GET /status` | Poll sync progress | Worker posts progress events persisted in IndexedDB |
| `GET /papers/random` | Return normalized paper | Client buffer selects DOI, fetches OpenAlex, caches paper locally |

## Non-functional expectations
- Offline-first behavior: config + journal snapshots + cached papers live in IndexedDB for reloads.
- Smooth UX: background worker maintains buffer of ~10 papers; UI remains responsive during sync.
- Config-driven theming: `text_size` updates CSS variables; settings overlay toggles without re-render flashes.
- Rate-limit aware networking: throttle Crossref/OpenAlex calls and support retries/backoff.
