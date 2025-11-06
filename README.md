# Paper Scroll

Doomscroll papers.

## Features

- Follow your favorite journals from Crossref
- Browse papers with metadata from OpenAlex
- Star papers for easy access later
- Export papers directly to Zotero

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
