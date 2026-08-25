import cv2
from pipeline import search_video

VIDEO_PATH = "video3.mp4"
TARGET = "I am going home"
FRAME_PATH = "result_frame.jpg"

print("Starting pipeline search...\n")

result = search_video(
    VIDEO_PATH,
    TARGET
)

if not result["found"]:
    print("❌ Target not found reliably.")
    exit()

if result["frame"] is not None:
    cv2.imwrite(FRAME_PATH, result["frame"])

timestamp = result["timestamp"]
hours = int(timestamp // 3600)
minutes = int((timestamp % 3600) // 60)
seconds = timestamp % 60
timestamp_string = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

print("""
===== RESULT =====
""")
print(f'Source Method: {result["source"]}')
print(f'Target       : "{result["target"]}"')
print(f'Matched      : "{result["matched_text"]}"')
print(f'Score        : {result["score"]:.2f}')
print(f'Start        : {timestamp_string}')
print(f'End          : {result["end_timestamp"]:.3f}s' if result["end_timestamp"] is not None else "End          : N/A")
print(f'Frame        : {result["frame_number"]}')
print(f'Image        : {FRAME_PATH}')
print("""
==================
""")
