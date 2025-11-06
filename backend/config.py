import os
from pathlib import Path
from typing import Final


DEFAULT_CONFIG: Final = {
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

CONFIG_FILENAME: Final = "config.json"
STARRED_DIRNAME: Final = "starred"
JOURNALS_DIRNAME: Final = "journals"


def resolve_storage_root() -> Path:
    """Resolve storage root for backend, defaulting to repo storage/data."""
    env_value = os.getenv("PAPER_SCROLL_STORAGE")
    if env_value:
        return Path(env_value).expanduser().resolve()
    # default path relative to project root
    return (Path.cwd() / "storage" / "data").resolve()
