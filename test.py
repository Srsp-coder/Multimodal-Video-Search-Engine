import whisper
import cv2
from rapidfuzz import fuzz

# ── CONFIG ──────────────────────────────────────────────
VIDEO_PATH = "video.mp4"        # change this to your video file path
TARGET     = "I am the danger"
FRAME_PATH = "result_frame.jpg"
# ────────────────────────────────────────────────────────


# STEP 1: Transcribe directly from video (no audio extraction needed)
print("Step 1: Transcribing video with Whisper...")
model  = whisper.load_model("base")
result = model.transcribe(VIDEO_PATH, word_timestamps=True, verbose=False)
print(f"Transcription done. Total segments: {len(result['segments'])}\n")


# STEP 2: Search for target dialogue
print("Step 2: Searching for target dialogue...")
target_clean = TARGET.lower().strip()
best_match   = None
best_score   = 0

for segment in result["segments"]:
    text  = segment["text"].lower().strip()
    score = fuzz.partial_ratio(target_clean, text)
    
    if score > best_score:
        best_score = score
        best_match = segment

print(f"Best score : {best_score}")
print(f"Best text  : {best_match['text']}")
print(f"Timestamp  : {best_match['start']:.3f}s\n")


# STEP 3: Extract exact frame
print("Step 3: Extracting frame from video...")
cap       = cv2.VideoCapture(VIDEO_PATH)
fps       = cap.get(cv2.CAP_PROP_FPS)
timestamp = best_match["start"]
frame_num = int(timestamp * fps)

print(f"FPS        : {fps}")
print(f"Frame num  : {frame_num}")

cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Could not extract frame")
    exit()


# STEP 4: Save frame and print output
print("Step 4: Saving result...\n")
cv2.imwrite(FRAME_PATH, frame)

hours   = int(timestamp // 3600)
minutes = int((timestamp % 3600) // 60)
seconds = timestamp % 60
ts_str  = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

print(f"""
===== RESULT =====
Timestamp : {ts_str}
Frame     : {frame_num}
Text      : "{best_match['text'].strip()}"
Score     : {best_score}
Image     : {FRAME_PATH}
==================
""")