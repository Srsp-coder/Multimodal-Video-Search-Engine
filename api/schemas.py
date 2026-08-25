from typing import Optional
from pydantic import BaseModel


class SearchResponse(BaseModel):
    found: bool
    source: Optional[str] = None
    target: str
    matched_text: Optional[str] = None
    score: float = 0.0
    timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    frame_number: Optional[int] = None
    video_path: Optional[str] = None
    frame_url: Optional[str] = None
