import whisper
import cv2
from rapidfuzz import fuzz

# ── CONFIG ──────────────────────────────────────────────
VIDEO_PATH = "video2.mp4"
TARGET = "whats bothering you"
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

# STEP 2: Combine words from ALL segments
print("Step 2: Building continuous word timeline...")

all_words = []

for segment in result["segments"]:

    words = segment.get("words", [])

    for word in words:

        all_words.append({
            "word": word["word"].strip(),
            "start": word["start"],
            "end": word["end"]
        })


print(f"Total words: {len(all_words)}\n")


# STEP 3: Search target across ALL words
print("Step 3: Searching for target dialogue...")

target_clean = TARGET.lower().strip()
target_words = target_clean.split()

best_score = 0
best_start = None
best_end = None
best_text = None


target_length = len(target_words)


for i in range(
    len(all_words) - target_length + 1
):

    # Take a window of the same number of words
    window = all_words[
        i:i + target_length
    ]

    window_text = " ".join(
        word["word"]
        for word in window
    ).lower()

    score = fuzz.ratio(
        target_clean,
        window_text
    )

    if score > best_score:

        best_score = score

        best_start = window[0]["start"]
        best_end = window[-1]["end"]

        best_text = window_text


# STEP 4: Check match
if (
    best_start is None
    or best_score < MATCH_THRESHOLD
):

    print("❌ Dialogue not found reliably.")
    print(f"Best score: {best_score:.2f}")

    exit()


print(f"Best score : {best_score:.2f}")
print(f"Matched text: {best_text}")
print(f"Start      : {best_start:.3f}s")
print(f"End        : {best_end:.3f}s\n")


# STEP 5: Extract frame
print("Step 4: Extracting frame from video...")

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

timestamp = best_start

frame_num = int(
    timestamp * fps
)

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


# STEP 6: Save frame
print("Step 5: Saving result...\n")

cv2.imwrite(
    FRAME_PATH,
    frame
)


# Convert timestamp to HH:MM:SS.mmm
hours = int(
    timestamp // 3600
)

minutes = int(
    (timestamp % 3600) // 60
)

seconds = timestamp % 60

ts_str = (
    f"{hours:02d}:"
    f"{minutes:02d}:"
    f"{seconds:06.3f}"
)


# STEP 7: Final output
print(f"""
===== RESULT =====

Target    : "{TARGET}"
Matched   : "{best_text}"

Score     : {best_score:.2f}

Start     : {ts_str}
End       : {best_end:.3f}s

Frame     : {frame_num}

Image     : {FRAME_PATH}

==================
""")