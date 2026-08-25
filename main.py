import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router

# Ensure required directories exist
for directory in ["downloads", "uploads", "results"]:
    os.makedirs(directory, exist_ok=True)

app = FastAPI(
    title="Quest1 Video Search API",
    description="API for dialogue and visual text search in video streams",
    version="1.0.0"
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

        timestamp = result["timestamp"]
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = timestamp % 60
        timestamp_string = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

        print("\n===== RESULT =====")
        print(f'Source Method: {result["source"]}')
        print(f'Target       : "{result["target"]}"')
        print(f'Matched      : "{result["matched_text"]}"')
        print(f'Score        : {result["score"]:.2f}')
        print(f'Start        : {timestamp_string}')
        print(f'End          : {result["end_timestamp"]:.3f}s' if result["end_timestamp"] is not None else "End          : N/A")
        print(f'Frame        : {result["frame_number"]}')
        print(f'Image        : {FRAME_PATH}')
        print("==================\n")
