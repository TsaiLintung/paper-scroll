from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .config import CONFIG_FILENAME, DEFAULT_CONFIG, JOURNALS_DIRNAME


class FileStorage:
    """Filesystem-backed storage for config and journal snapshots."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config_path = self.base_dir / CONFIG_FILENAME
        self.journals_dir = self.base_dir / JOURNALS_DIRNAME
        self._ensure_directories()

    # --- public API -------------------------------------------------

    def load_config(self) -> Dict:
        if not self.config_path.exists():
            self.save_config(DEFAULT_CONFIG.copy())
        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        normalized = self._normalize_config(data)
        if normalized != data:
            self.save_config(normalized)
        return normalized

    def save_config(self, config: Dict) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def journal_files(self) -> Iterable[Path]:
        yield from self.journals_dir.glob("*.json")

    def load_journal_items(self) -> List[Dict]:
        items = []
        for path in self.journal_files():
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            items.extend(data.get("items", []))
        return items

    def write_journal_snapshot(self, name: str, year: int, payload: Dict) -> Path:
        target = self.journals_dir / f"{name}-{year}.json"
        with target.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        return target

    def remove_journal_file(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    # --- helpers ----------------------------------------------------

    def _ensure_directories(self) -> None:
        for path in [self.base_dir, self.journals_dir]:
            path.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.save_config(DEFAULT_CONFIG.copy())

    @staticmethod
    def _normalize_config(data: Dict) -> Dict:
        normalized = DEFAULT_CONFIG.copy()
        normalized.update({k: v for k, v in data.items() if k in normalized})
        return normalized
