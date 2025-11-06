from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Journal(BaseModel):
    name: str = Field(..., min_length=1)
    issn: str = Field(..., min_length=8)


class ConfigPayload(BaseModel):
    start_year: int
    end_year: int
    text_size: int
    email: str = ""
    journals: List[Journal] = Field(default_factory=list)


class ConfigUpdate(BaseModel):
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    text_size: Optional[int] = None
    email: Optional[str] = None
    journals: Optional[List[Journal]] = None


class StatusResponse(BaseModel):
    message: str
    progress: float


class PaperResponse(BaseModel):
    paper: Dict[str, Any]
