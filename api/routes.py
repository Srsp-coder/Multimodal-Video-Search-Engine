import os
import uuid
import cv2
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from pipeline import search_video
from api.schemas import SearchResponse

router = APIRouter(prefix="/api", tags=["search"])

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"


@router.post("/search", response_model=SearchResponse)
async def search_endpoint(
    target: str = Form(...),
    url: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None)
):
    # Validation: exactly one video source supplied
    if url and video:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'url' or 'video', not both."
        )
    if not url and not video:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'url' or 'video' file."
        )

    source_path_or_url = None

    if video:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_ext = os.path.splitext(video.filename)[1] if video.filename else ".mp4"
        if not file_ext:
            file_ext = ".mp4"
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        saved_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            contents = await video.read()
            with open(saved_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save uploaded file: {str(e)}"
            )
        source_path_or_url = saved_path
    else:
        source_path_or_url = url.strip()

    # Execute search pipeline in threadpool
    try:
        result = await run_in_threadpool(
            search_video,
            source_path_or_url,
            target
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search pipeline error: {str(e)}"
        )

    frame_url = None
    frame_data = result.get("frame")

    if frame_data is not None:
        os.makedirs(RESULT_DIR, exist_ok=True)
        frame_filename = f"{uuid.uuid4().hex}.jpg"
        frame_file_path = os.path.join(RESULT_DIR, frame_filename)
        try:
            cv2.imwrite(frame_file_path, frame_data)
            frame_url = f"/api/results/{frame_filename}"
        except Exception as e:
            print(f"Warning: Failed to save frame image: {e}")

    return SearchResponse(
        found=result["found"],
        source=result["source"],
        target=result["target"],
        matched_text=result["matched_text"],
        score=result["score"],
        timestamp=result["timestamp"],
        end_timestamp=result["end_timestamp"],
        frame_number=result["frame_number"],
        video_path=result["video_path"],
        frame_url=frame_url
    )
