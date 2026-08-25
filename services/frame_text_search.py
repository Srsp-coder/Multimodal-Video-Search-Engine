import cv2
import easyocr
from rapidfuzz import fuzz

_ocr_reader = None


def get_ocr_reader(lang_list=None, gpu=True):
    global _ocr_reader
    if _ocr_reader is None:
        if lang_list is None:
            lang_list = ["en"]
        try:
            _ocr_reader = easyocr.Reader(lang_list, gpu=gpu)
        except Exception:
            _ocr_reader = easyocr.Reader(lang_list, gpu=False)
    return _ocr_reader


def preprocess_frame(frame, upscale_factor=2.0, apply_clahe=True):
    """
    Enhance frame for EasyOCR readability (especially low-resolution videos like 144p).
    - Upscaling (INTER_CUBIC)
    - Grayscale conversion
    - CLAHE contrast enhancement
    """
    if frame is None or frame.size == 0:
        return frame

    h, w = frame.shape[:2]

    if h < 240:
        upscale_factor = max(upscale_factor, 3.0)
    elif h < 480:
        upscale_factor = max(upscale_factor, 2.0)
    else:
        upscale_factor = 1.0

    if upscale_factor > 1.0:
        new_w = int(w * upscale_factor)
        new_h = int(h * upscale_factor)
        processed = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    else:
        processed = frame.copy()

    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    if apply_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
    else:
        enhanced = gray

    return enhanced


def match_ocr_text(target, detected_text):
    """
    Robust similarity matching protecting against false positives from single-char or short OCR noise.
    """
    target_clean = target.lower().strip()
    text_clean = detected_text.lower().strip()

    if not target_clean or not text_clean:
        return 0.0

    partial_score = fuzz.partial_ratio(target_clean, text_clean)
    ratio_score = fuzz.ratio(target_clean, text_clean)
    token_set_score = fuzz.token_set_ratio(target_clean, text_clean)

    target_words = target_clean.split()
    text_words = text_clean.split()

    # Guard against tiny text false positives (e.g. target: "In my younger age", OCR: "M")
    if len(target_words) > 1 and len(text_words) == 1 and len(text_clean) < 4:
        return 0.0

    len_ratio = len(text_clean) / max(1, len(target_clean))
    if len_ratio < 0.25 and len(target_clean) > 5:
        partial_score *= len_ratio

    if len(target_words) > 1:
        matching_words = sum(1 for tw in target_words if any(fuzz.ratio(tw, dw) > 75 for dw in text_words))
        word_ratio = matching_words / len(target_words)
        if word_ratio < 0.33:
            return 0.0

    weighted_score = (partial_score * 0.4 + token_set_score * 0.4 + ratio_score * 0.2)
    return weighted_score


def search_frames(
    video_path,
    target,
    sample_interval=0.5,
    threshold=70,
    preprocess=True,
    fine_refine=True
):
    print("Initializing OCR model...")
    reader = get_ocr_reader(["en"], gpu=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError("Could not open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps if fps > 0 else 0.0

    print(f"FPS      : {fps}")
    print(f"Duration : {duration:.2f}s")
    print(f"Sampling : every {sample_interval}s\n")

    best_match = None
    best_score = 0.0

    current_time = 0.0

    while current_time < duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)
        ret, frame = cap.read()
        if not ret:
            break

        frame_to_ocr = preprocess_frame(frame) if preprocess else frame
        results = reader.readtext(frame_to_ocr)

        detected_text = " ".join(res[1] for res in results if len(res) > 1)

        if detected_text.strip():
            score = match_ocr_text(target, detected_text)
            print(f"[{current_time:.2f}s] Detected: '{detected_text}' (Score: {score:.1f})")

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

    # Two-stage refinement around coarse candidate if enabled
    if fine_refine and best_match is not None and best_score >= threshold:
        coarse_time = best_match["timestamp"]
        fine_start = max(0.0, coarse_time - sample_interval)
        fine_end = min(duration, coarse_time + sample_interval)
        fine_step = max(0.05, sample_interval / 5.0)

        t = fine_start
        earliest_time = coarse_time
        earliest_frame = best_match["frame"]
        earliest_text = best_match["text"]
        earliest_score = best_score

        while t < fine_end:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = cap.read()
            if ret:
                frame_to_ocr = preprocess_frame(frame) if preprocess else frame
                results = reader.readtext(frame_to_ocr)
                detected_text = " ".join(res[1] for res in results if len(res) > 1)
                score = match_ocr_text(target, detected_text)
                if score >= threshold:
                    earliest_time = t
                    earliest_frame = frame.copy()
                    earliest_text = detected_text
                    earliest_score = score
                    break
            t += fine_step

        best_match["timestamp"] = earliest_time
        best_match["frame_number"] = int(earliest_time * fps)
        best_match["frame"] = earliest_frame
        best_match["text"] = earliest_text
        best_match["score"] = max(best_score, earliest_score)

    cap.release()

    if best_match is None or best_score < threshold:
        return None

    return best_match