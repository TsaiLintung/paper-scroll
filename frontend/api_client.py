from __future__ import annotations

import os
import threading
import time
from typing import Callable, List, Optional, Tuple

import requests

from .paper import Paper

DEFAULT_API_URL = os.getenv("PAPER_SCROLL_API_URL", "http://127.0.0.1:8000")
DEFAULT_CONFIG = {
    "start_year": 2021,
    "end_year": 2021,
    "text_size": 16,
    "email": "",
    "zotero_key": "",
    "zotero_id": "",
    "journals": [
        {"name": "aer", "issn": "0002-8282"}
    ],
}


class BackendUnavailableError(Exception):
    """Raised when the FastAPI backend cannot be reached."""


class ApiClient:
    """HTTP client responsible for talking to the FastAPI backend."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or DEFAULT_API_URL
        self.session = requests.Session()
        self.config = DEFAULT_CONFIG.copy()
        self.available = False
        self._status_callback: Optional[Callable[[Tuple[str, float]], None]] = None
        try:
            self.refresh_config()
        except BackendUnavailableError:
            # Leave defaults in place; UI will react to availability later.
            pass

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def set_status_callback(self, callback: Callable[[Tuple[str, float]], None]) -> None:
        self._status_callback = callback

    def refresh_config(self) -> dict:
        try:
            response = self._request("GET", "/config", timeout=30)
        except BackendUnavailableError:
            return self.config
        self.config = response.json()
        return self.config

    def _patch_config(self, payload: dict) -> dict:
        response = self._request("PATCH", "/config", json=payload, timeout=30)
        self.config = response.json()
        return self.config

    def update_config(self, field: str, value) -> None:
        self._patch_config({field: value})

    def add_journal(self, name: str, issn: str) -> None:
        response = self._request(
            "POST", "/journals", json={"name": name, "issn": issn}, timeout=30
        )
        self.config = response.json()

    def remove_journal(self, issn: str) -> None:
        response = self._request("DELETE", f"/journals/{issn}", timeout=30)
        self.config = response.json()

    # ------------------------------------------------------------------
    # Status / Sync
    # ------------------------------------------------------------------

    def update_journals(self, *_args, **_kwargs) -> None:
        """Kick off journal sync and poll status until done."""

        def worker():
            try:
                self._request("POST", "/journals/sync", timeout=10)
            except BackendUnavailableError as exc:
                self._emit_status(str(exc), 0.0)
                return

            while True:
                time.sleep(1.0)
                try:
                    status_response = self._request("GET", "/status", timeout=10)
                except BackendUnavailableError as exc:
                    self._emit_status(str(exc), 0.0)
                    break
                status_payload = status_response.json()
                self._emit_status(
                    status_payload.get("message", ""),
                    float(status_payload.get("progress", 0.0)),
                )
                if status_payload.get("progress", 0) >= 1:
                    break

            # Refresh local cache once sync completes
            try:
                self.refresh_config()
            except BackendUnavailableError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _emit_status(self, message: str, progress: float) -> None:
        if self._status_callback:
            self._status_callback((message, progress))

    def _request(self, method: str, path: str, timeout: int = 30, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            self.available = True
            return response
        except requests.RequestException as exc:
            self.available = False
            raise BackendUnavailableError(
                f"Backend unavailable at {self.base_url}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Papers
    # ------------------------------------------------------------------

    def get_random_paper(self) -> Paper:
        response = self._request("GET", "/papers/random", timeout=30)
        payload = response.json()
        return Paper(payload["paper"])

    def get_starred_papers(self) -> List[Paper]:
        response = self._request("GET", "/papers/starred", timeout=30)
        payload = response.json()
        return [Paper(item) for item in payload.get("papers", [])]

    def star(self, paper: Paper) -> None:
        self._request(
            "POST",
            "/papers/star",
            json={"paper": paper.data},
            timeout=30,
        )

    def unstar(self, paper: Paper) -> None:
        doi = paper.get("doi", "")
        self._request("DELETE", f"/papers/star/{doi}", timeout=30)

    def on_star_change(self, paper: Paper, new_status: bool) -> None:
        if new_status:
            self.star(paper)
        else:
            self.unstar(paper)

    def export_paper_to_zotero(self, paper: Paper) -> None:
        self._request(
            "POST",
            "/papers/export",
            json={"paper": paper.data},
            timeout=60,
        )
