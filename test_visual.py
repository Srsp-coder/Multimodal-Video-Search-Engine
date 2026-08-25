import cv2

from services.frame_text_search import (
    search_frames
)


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

VIDEO_PATH = "video5.mp4"

TARGET = "In my younger age"

FRAME_PATH = "visual_match.jpg"

MATCH_THRESHOLD = 70


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

print("Starting visual OCR search...\n")


result = search_frames(
    video_path=VIDEO_PATH,
    target=TARGET,
    threshold=MATCH_THRESHOLD
)


if result is None:

    print(
        "❌ Target text was not found reliably."
    )

    exit()


# ---------------------------------------------------------
# Save final frame
# ---------------------------------------------------------

cv2.imwrite(
    FRAME_PATH,
    result["frame"]
)


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------

timestamp = result["timestamp"]

hours = int(
    timestamp // 3600
)

minutes = int(
    (timestamp % 3600) // 60
)

seconds = timestamp % 60

timestamp_string = (
    f"{hours:02d}:"
    f"{minutes:02d}:"
    f"{seconds:06.3f}"
)


print("===== VISUAL SEARCH RESULT =====")

print(
    f'Target    : "{TARGET}"'
)

print(
    f'Detected  : "{result["text"]}"'
)

print(
    f'Score     : {result["score"]:.2f}'
)

print(
    f"Timestamp : {timestamp_string}"
)

print(
    f"Frame     : {result['frame_number']}"
)

print(
    f"Image     : {FRAME_PATH}"
)

print("================================")