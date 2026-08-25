import cv2

from pipeline import process_video


VIDEO_PATH = "video2.mp4"
TARGET = "and i refused"
FRAME_PATH = "result_frame.jpg"


print("Starting dialogue search...\n")


result = process_video(
    VIDEO_PATH,
    TARGET
)


if result is None:

    print("❌ Dialogue not found reliably.")
    exit()


# Save extracted frame
cv2.imwrite(
    FRAME_PATH,
    result["frame"]
)


# Format timestamp
timestamp = result["start"]

hours = int(timestamp // 3600)

minutes = int(
    (timestamp % 3600) // 60
)

seconds = timestamp % 60

timestamp_string = (
    f"{hours:02d}:"
    f"{minutes:02d}:"
    f"{seconds:06.3f}"
)


print("""
===== RESULT =====
""")

print(f'Target    : "{TARGET}"')
print(f'Matched   : "{result["text"]}"')
print(f'Score     : {result["score"]:.2f}')
print(f'Start     : {timestamp_string}')
print(f'End       : {result["end"]:.3f}s')
print(f'Frame     : {result["frame_num"]}')
print(f'Image     : {FRAME_PATH}')

print("""
==================
""")