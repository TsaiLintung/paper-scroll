from __future__ import annotations

import random
import threading
import time
from typing import Dict, List, Optional, Tuple

import requests

from .storage import FileStorage

DEFAULT_PAPER = {"DOI": "10.1038/s41586-020-2649-2"}
BUFFER_SIZE = 10


class BackendService:
    """Core domain service decoupled from the Flet UI."""

    def __init__(self, storage: FileStorage):
        self.storage = storage
        self.config = self.storage.load_config()
        self._paper_buffer: List[Dict] = []
        self._buffer_thread: Optional[threading.Thread] = None
        self._papers: List[Dict] = []
        self._status: Tuple[str, float] = ("Idle", 0.0)
        self._status_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        self._load_indexed_papers()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def get_config(self) -> Dict:
        return self.config

    def update_config(self, updates: Dict) -> Dict:
        """Apply config updates and persist them."""
        self.config.update({k: v for k, v in updates.items() if v is not None})
        self.storage.save_config(self.config)
        return self.config

    def add_journal(self, name: str, issn: str) -> Dict:
        journals = self.config.setdefault("journals", [])
        if not any(j["issn"] == issn for j in journals):
            journals.append({"name": name, "issn": issn})
            self.storage.save_config(self.config)
        return self.config

    def remove_journal(self, issn: str) -> Dict:
        journals = self.config.get("journals", [])
        self.config["journals"] = [j for j in journals if j.get("issn") != issn]
        self.storage.save_config(self.config)
        return self.config

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def set_status(self, message: str, progress: float) -> None:
        with self._status_lock:
            self._status = (message, progress)

    def get_status(self) -> Tuple[str, float]:
        with self._status_lock:
            return self._status

    # ------------------------------------------------------------------
    # Journals / Papers
    # ------------------------------------------------------------------

    def sync_journals(self) -> None:
        """Fetch papers from Crossref for configured journals."""
        start_year = self.config.get("start_year", 2021)
        end_year = self.config.get("end_year", start_year)
        journals = self.config.get("journals", [])

        allowed_names = {journal["name"] for journal in journals}
        for path in list(self.storage.journal_files()):
            stem = path.stem
            parts = stem.split("-")
            journal_name = "-".join(parts[:-1]) if len(parts) > 1 else stem
            year_str = parts[-1] if parts else ""
            remove = (
                journal_name not in allowed_names
                or not year_str.isdigit()
                or not (start_year <= int(year_str) <= end_year)
            )
            if remove:
                self.storage.remove_journal_file(path)

        to_fetch: List[Tuple[Dict, int]] = []
        for journal in journals:
            for year in range(start_year, end_year + 1):
                to_fetch.append((journal, year))

        total = len(to_fetch)
        if total == 0:
            self.set_status("No journals configured.", 1.0)
            return

        for index, (journal, year) in enumerate(to_fetch, start=1):
            target_path = self.storage.journals_dir / f"{journal['name']}-{year}.json"
            if target_path.exists():
                continue
            items = self._fetch_crossref_journal_year(journal["issn"], year)
            payload = {
                "issn": journal["issn"],
                "name": journal["name"],
                "year": year,
                "items": [{"DOI": item.get("DOI")} for item in items],
            }
            self.storage.write_journal_snapshot(journal["name"], year, payload)
            progress = index / total
            self.set_status(
                f"Fetched {len(items)} papers for {journal['name']} in {year}.",
                progress,
            )

        self._load_indexed_papers()
        self.set_status("All journals updated.", 1.0)

    def get_random_paper(self) -> Dict:
        with self._buffer_lock:
            if not self._paper_buffer:
                paper = self._load_random_paper()
                self._paper_buffer.append(paper)
            paper = self._paper_buffer.pop(0)
        self._ensure_buffer()
        return paper


    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_indexed_papers(self) -> None:
        self._papers = self.storage.load_journal_items()
        if not self._papers:
            self._papers = [DEFAULT_PAPER]

    def _fetch_crossref_journal_year(self, journal_issn: str, year: int) -> List[Dict]:
        items = []
        cursor = "*"
        batch_size = 200
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        while True:
            url = (
                f"https://api.crossref.org/journals/"
                f"{journal_issn}/works/"
                f"?filter=from-pub-date:{start_date},until-pub-date:{end_date}"
                f"&rows={batch_size}&cursor={cursor}"
            )
            resp = requests.get(url, timeout=100)
            resp.raise_for_status()
            data = resp.json()
            message = data.get("message", {})
            batch = message.get("items", [])
            items.extend(batch)
            next_cursor = message.get("next-cursor")
            if not next_cursor or not batch:
                break
            cursor = next_cursor
            time.sleep(0.5)
        return items

    def _load_random_paper(self) -> Dict:
        while True:
            doi_entry = random.choice(self._papers)
            doi = doi_entry.get("DOI")
            if not doi:
                continue
            url = f"https://api.openalex.org/works/https://doi.org/{doi}"
            email = self.config.get("email")
            if email:
                url += f"?mailto={email}"
            try:
                resp = requests.get(url, timeout=100)
                if resp.status_code != 200:
                    continue
                paper = resp.json()
                if paper:
                    return paper
            except Exception:
                continue

    def _ensure_buffer(self) -> None:
        def buffer_worker():
            while True:
                with self._buffer_lock:
                    if len(self._paper_buffer) >= BUFFER_SIZE:
                        break
                paper = self._load_random_paper()
                with self._buffer_lock:
                    if len(self._paper_buffer) < BUFFER_SIZE:
                        self._paper_buffer.append(paper)

        if not self._buffer_thread or not self._buffer_thread.is_alive():
            self._buffer_thread = threading.Thread(target=buffer_worker, daemon=True)
            self._buffer_thread.start()
