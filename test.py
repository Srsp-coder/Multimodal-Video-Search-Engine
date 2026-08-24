import whisper
import cv2
from rapidfuzz import fuzz

# ── CONFIG ──────────────────────────────────────────────
VIDEO_PATH = "video.mp4"
TARGET = "let's both of us stop trying to justify this whole thing and admit you're in danger."
FRAME_PATH = "result_frame.jpg"

MATCH_THRESHOLD = 70
# ────────────────────────────────────────────────────────


# STEP 1: Transcribe video
print("Step 1: Transcribing video with Whisper...")

model = whisper.load_model("base")

result = model.transcribe(
    VIDEO_PATH,
    word_timestamps=True,
    verbose=False
)

print(
    f"Transcription done. "
    f"Total segments: {len(result['segments'])}\n"
)
for dict in result['segments']:
    print(dict['text'])


# STEP 2: Search target using word timestamps
print("Step 2: Searching for target dialogue...")

target_clean = TARGET.lower().strip()
target_words = target_clean.split()

best_score = 0
best_start = None
best_end = None
best_text = None


for segment in result["segments"]:

    words = segment.get("words", [])

    if not words:
        continue

    # Extract words from this segment
    segment_words = [
        word["word"].strip()
        for word in words
    ]

    # Try different windows around the target length
    target_length = len(target_words)

    for i in range(len(segment_words) - target_length + 1):

        window_words = segment_words[
            i:i + target_length
        ]

        window_text = " ".join(window_words).lower()

        score = fuzz.ratio(
            target_clean,
            window_text
        )

        if score > best_score:

            best_score = score

            # Timestamp of FIRST word in match
            best_start = words[i]["start"]

            # Timestamp of LAST word in match
            best_end = words[
                i + target_length - 1
            ]["end"]

            best_text = window_text


# STEP 3: Check whether a good match was found
if best_start is None or best_score < MATCH_THRESHOLD:

    print("❌ Dialogue not found reliably.")
    print(f"Best score: {best_score}")

    exit()


print(f"Best score : {best_score:.1f}")
print(f"Matched text: {best_text}")
print(f"Start      : {best_start:.3f}s")
print(f"End        : {best_end:.3f}s\n")


# STEP 4: Extract exact frame
print("Step 3: Extracting frame from video...")

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

timestamp = best_start

frame_num = int(timestamp * fps)

print(f"FPS        : {fps}")
print(f"Frame num  : {frame_num}")
print(f"Timestamp  : {timestamp:.3f}s")


cap.set(
    cv2.CAP_PROP_POS_FRAMES,
    frame_num
)

ret, frame = cap.read()

cap.release()


if not ret:

    print("❌ Could not extract frame")

    exit()


# STEP 5: Save frame
print("Step 4: Saving result...\n")

cv2.imwrite(
    FRAME_PATH,
    frame
)


# Convert timestamp to HH:MM:SS.mmm
hours = int(timestamp // 3600)

minutes = int(
    (timestamp % 3600) // 60
)

seconds = timestamp % 60

ts_str = (
    f"{hours:02d}:"
    f"{minutes:02d}:"
    f"{seconds:06.3f}"
)


# STEP 6: Final output
print(f"""
===== RESULT =====

Target    : "{TARGET}"
Matched   : "{best_text}"

Score     : {best_score:.1f}

Start     : {ts_str}
End       : {best_end:.3f}s

Frame     : {frame_num}

Image     : {FRAME_PATH}

==================
""")