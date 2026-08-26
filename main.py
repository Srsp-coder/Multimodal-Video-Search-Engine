import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router

from fastapi.middleware.cors import CORSMiddleware

# Ensure required directories exist
for directory in ["downloads", "uploads", "results"]:
    os.makedirs(directory, exist_ok=True)

app = FastAPI(
    title="Quest1 Video Search API",
    description="API for dialogue and visual text search in video streams",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve persistent result images
app.mount("/api/results", StaticFiles(directory="results"), name="results")

# Include API routes
app.include_router(api_router)


if __name__ == "__main__":
    # CLI runner mode when executed directly
    import cv2
    from pipeline import search_video

    VIDEO_PATH = "video5.mp4"
    TARGET = "crossed 50 yrs"
    FRAME_PATH = "result_frame.jpg"

    print("Starting pipeline search (CLI mode)...\n")

    result = search_video(
        VIDEO_PATH,
        TARGET
    )

    if not result["found"]:
        print("❌ Target not found reliably.")
    else:
        if result["frame"] is not None:
            cv2.imwrite(FRAME_PATH, result["frame"])

        print("\n===== RESULT =====")
        print(f'Source Method: {result["source"]}')
        print(f'Target       : "{result["target"]}"')
        print(f'Matched      : "{result["matched_text"]}"')
        print(f'Score        : {result["score"]:.2f}')
        print(f'Start        : {result["timestamp"]}')
        print(f'End          : {result["end_timestamp"]}' if result["end_timestamp"] is not None else "End          : N/A")
        print(f'Frame        : {result["frame_number"]}')
        print(f'Image        : {FRAME_PATH}')
        print("==================\n")
