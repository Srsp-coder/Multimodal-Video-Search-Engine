from typing import Optional, Union
from pydantic import BaseModel


class SearchResponse(BaseModel):
    found: bool
    source: Optional[str] = None
    target: str
    matched_text: Optional[str] = None
    score: float = 0.0
    timestamp: Optional[Union[str, float]] = None
    end_timestamp: Optional[Union[str, float]] = None
    frame_number: Optional[int] = None
    video_path: Optional[str] = None
    frame_url: Optional[str] = None

