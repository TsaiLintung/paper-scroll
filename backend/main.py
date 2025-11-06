from __future__ import annotations

from typing import Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import resolve_storage_root
from .schemas import (
    ConfigPayload,
    ConfigUpdate,
    PaperPayload,
    PaperResponse,
    StarredPaperResponse,
    StatusResponse,
)
from .services import BackendService
from .storage import FileStorage

storage = FileStorage(resolve_storage_root())
service = BackendService(storage)

app = FastAPI(title="Paper Scroll Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/config", response_model=ConfigPayload)
def read_config() -> Dict:
    return service.get_config()


@app.patch("/config", response_model=ConfigPayload)
def patch_config(payload: ConfigUpdate) -> Dict:
    return service.update_config(payload.model_dump(exclude_none=True))


@app.post("/journals", response_model=ConfigPayload, status_code=status.HTTP_201_CREATED)
def add_journal(payload: Dict[str, str]) -> Dict:
    name = payload.get("name")
    issn = payload.get("issn")
    if not name or not issn:
        raise HTTPException(status_code=400, detail="Both name and ISSN are required.")
    return service.add_journal(name, issn)


@app.delete("/journals/{issn}", response_model=ConfigPayload)
def delete_journal(issn: str) -> Dict:
    return service.remove_journal(issn)


@app.post("/journals/sync", status_code=status.HTTP_202_ACCEPTED)
def sync_journals(background_tasks: BackgroundTasks) -> StatusResponse:
    background_tasks.add_task(service.sync_journals)
    return StatusResponse(message="Sync started.", progress=0.0)


@app.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    message, progress = service.get_status()
    return StatusResponse(message=message, progress=progress)


@app.get("/papers/random", response_model=PaperResponse)
def random_paper() -> PaperResponse:
    return PaperResponse(paper=service.get_random_paper())


@app.get("/papers/starred", response_model=StarredPaperResponse)
def starred_papers() -> StarredPaperResponse:
    return StarredPaperResponse(papers=service.list_starred_papers())


@app.post("/papers/star", status_code=status.HTTP_200_OK)
def star_paper(payload: PaperPayload) -> Dict[str, str]:
    paper = payload.paper
    if "doi" not in paper:
        raise HTTPException(status_code=400, detail="Paper DOI is required.")
    service.star_paper(paper)
    return {"status": "starred"}


@app.delete("/papers/star/{doi}", status_code=status.HTTP_200_OK)
def unstar_paper(doi: str) -> Dict[str, str]:
    service.unstar_paper(doi)
    return {"status": "unstarred"}


@app.get("/papers/star/{doi}")
def is_starred(doi: str) -> Dict[str, bool]:
    return {"starred": service.is_starred(doi)}


@app.post("/papers/export", response_model=StatusResponse)
def export_to_zotero(payload: PaperPayload) -> StatusResponse:
    success, message = service.export_to_zotero(payload.paper)
    progress = 1.0 if success else 0.0
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return StatusResponse(message=message, progress=progress)
