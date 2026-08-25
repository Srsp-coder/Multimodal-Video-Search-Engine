import cv2
import easyocr
from rapidfuzz import fuzz


def search_frames(
    video_path,
    target,
    sample_interval=1.0,
    threshold=70
):

    print("Loading OCR model...")

    reader = easyocr.Reader(
        ["en"],
        gpu=True
    )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open video."
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    total_frames = cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )

    duration = (
        total_frames / fps
        if fps > 0
        else 0
    )

    print(f"FPS      : {fps}")
    print(f"Duration : {duration:.2f}s")
    print(
        f"Sampling : every {sample_interval}s\n"
    )

    best_match = None
    best_score = 0

    current_time = 0.0

    while current_time < duration:

        cap.set(
            cv2.CAP_PROP_POS_MSEC,
            current_time * 1000
        )

        ret, frame = cap.read()

        if not ret:
            break

        results = reader.readtext(frame)

        detected_text = " ".join(
            result[1]
            for result in results
        )

        if detected_text.strip():

            print(
                f"[{current_time:.2f}s] "
                f"{detected_text}"
            )

            score = fuzz.partial_ratio(
                target.lower(),
                detected_text.lower()
            )

            if score > best_score:

                best_score = score
                frame_number = int(current_time * fps)
                best_match = {
                "text": detected_text,
                "score": score,
                "timestamp": current_time,
                "frame_number": frame_number,
                "frame": frame.copy()
                }

        current_time += sample_interval

    cap.release()

    if (
        best_match is None
        or best_score < threshold
    ):

        return None

    return best_match