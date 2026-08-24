import whisper
import yt_dlp
import cv2
import subprocess
from rapidfuzz import fuzz

# ── CONFIG ──────────────────────────────────────────────
VIDEO_URL      = "https://ok.ru/video/248244667877"
TARGET         = "My mind rebels at stagnation"
VIDEO_PATH     = "video.mp4"
AUDIO_PATH     = "audio.wav"
# ────────────────────────────────────────────────────────


# STEP 1: Download
print("Step 1: Downloading video...")
ydl_opts = {
    'outtmpl': VIDEO_PATH,
    'format': 'best[ext=mp4]/best',
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([VIDEO_URL])
print("Done\n")


# STEP 2: Extract Audio
print("Step 2: Extracting audio...")
subprocess.run([
    "ffmpeg", "-i", VIDEO_PATH,
    "-ar", "16000",
    "-ac", "1",
    "-y",
    AUDIO_PATH
], check=True)
print("Done\n")


# STEP 3: Transcribe
print("Step 3: Transcribing with Whisper (this may take a few mins)...")
model = whisper.load_model("base")
result = model.transcribe(AUDIO_PATH, word_timestamps=True, verbose=False)
print("Done\n")


# STEP 4: Match
print("Step 4: Searching for target dialogue...")
target_clean = TARGET.lower().strip()
best_match   = None
best_score   = 0

for segment in result["segments"]:
    text  = segment["text"].lower().strip()
    score = fuzz.partial_ratio(target_clean, text)
    if score > best_score:
        best_score = score
        best_match = segment

print(f"Best match score : {best_score}")
print(f"Best match text  : {best_match['text']}")
print(f"Timestamp        : {best_match['start']:.3f}s\n")


# STEP 5: Get Frame
print("Step 5: Extracting frame...")
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
timestamp  = best_match["start"]
frame_num  = int(timestamp * fps)

cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
ret, frame = cap.read()
cap.release()
print(f"FPS: {fps}, Frame number: {frame_num}\n")


# STEP 6: Output
print("Step 6: Saving output...")
hours   = int(timestamp // 3600)
minutes = int((timestamp % 3600) // 60)
seconds = timestamp % 60
ts_str  = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

image_path = f"result_frame_{frame_num}.jpg"
cv2.imwrite(image_path, frame)

print(f"""
===== RESULT =====
Timestamp : {ts_str}
Frame     : {frame_num}
Text      : "{best_match['text'].strip()}"
Image     : {image_path}
==================
""")