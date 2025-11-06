# Paper Scroll

Doomscroll papers.

## Features

- Follow your favorite journals from Crossref
- Browse papers with metadata from OpenAlex
- Launch full abstracts and open-access links directly from the app

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/TsaiLintung/paper-scroll.git
   ```
2. Install dependencies (Python 3.13+ required):
   ```sh
   poetry install
   ```

## Usage

1. Start the FastAPI backend:
   ```sh
   poetry run uvicorn backend.main:app --reload
   ```
   The server defaults to `http://127.0.0.1:8000`. Override with `PAPER_SCROLL_API_URL`.
2. In a separate terminal, launch the Flet client:
   ```sh
   poetry run flet run
   ```

## Project Structure
- `backend/` — FastAPI service exposing paper, journal, and config endpoints
- `frontend/` — Flet UI components and API client
- `main.py` — Flet entry point that wires the frontend to the backend

## Upgrading from Earlier Versions

Older builds supported starring papers and exporting to Zotero. Those capabilities have been removed; you can safely delete any legacy files left under `storage/data/starred/` and drop `zotero_*` keys from `storage/data/config.json` if they remain.
