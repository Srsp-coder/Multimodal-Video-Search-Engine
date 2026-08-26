import os
import cv2

from services.video_downloader import download_video
from services.subtitle_search import search_video_subtitle
from services.transcription import (
    transcribe_video,
    build_word_timeline,
    verify_audio_window
)
from services.dialogue_search import search_dialogue
from services.frame_text_search import search_frames
from services.frame_extractor import extract_frame


def format_timestamp(seconds):
    if seconds is None:
        return None
    total_ms = round(seconds * 1000)
    hours = total_ms // 3600000
    rem = total_ms % 3600000
    minutes = rem // 60000
    rem %= 60000
    secs = rem // 1000
    millis = rem % 1000
    return f"{hours}:{minutes:02d}:{secs:02d}.{millis:03d}"


def make_empty_result(video_path, target):
    return {
        "found": False,
        "source": None,
        "target": target,
        "matched_text": None,
        "score": 0.0,
        "timestamp": None,
        "end_timestamp": None,
        "frame_number": None,
        "frame": None,
        "video_path": video_path
    }


def search_video(
    source: str,
    target: str,
    threshold: float = 70.0,
    verification_window: float = 5.0,
    ocr_sample_interval: float = 0.5,
    ocr_preprocess: bool = True
) -> dict:
    """
    Main orchestration pipeline for video dialogue & visual text search.
    Search priority: SUBTITLES -> WHISPER/AUDIO -> OCR -> FRAME EXTRACTION
    """
    print(f"\n[PIPELINE] Resolving input source: '{source}'")

    # 1. Resolve Input
    if source.startswith(("http://", "https://")):
        print("[PIPELINE] Input type: URL")
        try:
            video_path = download_video(source)
            print(f"[PIPELINE] Download complete: {video_path}")
        except Exception as e:
            print(f"[PIPELINE] Failed to download video from URL: {e}")
            return make_empty_result(source, target)
    else:
        print("[PIPELINE] Input type: Local File")
        video_path = source

    if not os.path.exists(video_path):
        print(f"[PIPELINE] Video file does not exist: {video_path}")
        return make_empty_result(video_path, target)

    # Validate Video opening
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[PIPELINE] Video file exists but cannot be opened: {video_path}")
        cap.release()
        return make_empty_result(video_path, target)
    cap.release()

    # 2. Subtitle Search
    print("[PIPELINE] Searching subtitles...")
    sub_match = None
    try:
        sub_source = source if source.startswith(("http://", "https://")) else video_path
        sub_match = search_video_subtitle(sub_source, target, threshold=threshold)
    except Exception as e:
        print(f"[PIPELINE] Subtitle search error (continuing): {e}")

    if sub_match is not None:
        candidate_start = sub_match["start"]
        candidate_end = sub_match["end"]
        print(f"[PIPELINE] Subtitle candidate found at {candidate_start:.2f}s (Score: {sub_match['score']:.1f})")
        print(f"[PIPELINE] Verifying candidate with Whisper ({verification_window}s window)...")

        v_match = None
        try:
            v_match = verify_audio_window(
                video_path,
                target,
                candidate_start,
                candidate_end,
                window=verification_window
            )
        except Exception as e:
            print(f"[PIPELINE] Candidate audio verification error: {e}")

        if v_match is not None:
            print("[PIPELINE] Verification successful!")
            final_start = v_match["start"]
            final_end = v_match["end"]
            frame, frame_num = extract_frame(video_path, final_start)
            return {
                "found": True,
                "source": "subtitle",
                "target": target,
                "matched_text": v_match["text"],
                "score": float(v_match["score"]),
                "timestamp": format_timestamp(final_start),
                "end_timestamp": format_timestamp(final_end),
                "frame_number": frame_num,
                "frame": frame,
                "video_path": video_path
            }
        else:
            print("[PIPELINE] Verification unconfirmed. Proceeding to full Whisper search...")
    else:
        print("[PIPELINE] No matching subtitle found.")

    # 3. Whisper Audio Fallback
    print("[PIPELINE] Executing full Whisper audio search...")
    w_match = None
    try:
        transcription_result = transcribe_video(video_path)
        words = build_word_timeline(transcription_result)
        w_match = search_dialogue(words, target, threshold=threshold)
    except Exception as e:
        print(f"[PIPELINE] Whisper search error (continuing): {e}")

    if w_match is not None:
        print(f"[PIPELINE] Whisper match found at {w_match['start']:.2f}s (Score: {w_match['score']:.1f})")
        final_start = w_match["start"]
        final_end = w_match["end"]
        frame, frame_num = extract_frame(video_path, final_start)
        return {
            "found": True,
            "source": "whisper",
            "target": target,
            "matched_text": w_match["text"],
            "score": float(w_match["score"]),
            "timestamp": format_timestamp(final_start),
            "end_timestamp": format_timestamp(final_end),
            "frame_number": frame_num,
            "frame": frame,
            "video_path": video_path
        }
    else:
        print("[PIPELINE] Whisper audio search yielded no match.")

    # 4. OCR Visual Fallback
    print("[PIPELINE] Executing OCR visual search...")
    ocr_match = None
    try:
        ocr_match = search_frames(
            video_path=video_path,
            target=target,
            sample_interval=ocr_sample_interval,
            threshold=threshold,
            preprocess=ocr_preprocess,
            fine_refine=True
        )
    except Exception as e:
        print(f"[PIPELINE] OCR search error: {e}")

    if ocr_match is not None:
        timestamp = ocr_match["timestamp"]
        print(f"[PIPELINE] OCR match found at {timestamp:.2f}s (Score: {ocr_match['score']:.1f})")
        frame, frame_num = extract_frame(video_path, timestamp)
        return {
            "found": True,
            "source": "ocr",
            "target": target,
            "matched_text": ocr_match["text"],
            "score": float(ocr_match["score"]),
            "timestamp": format_timestamp(timestamp),
            "end_timestamp": format_timestamp(timestamp),
            "frame_number": frame_num,
            "frame": frame,
            "video_path": video_path
        }

    print("[PIPELINE] Target search completed: Not found in subtitles, audio, or visual frames.")
    return make_empty_result(video_path, target)


def process_video(video_path, target):
    """
    Backward compatibility helper mapping search_video to previous return format.
    """
    res = search_video(video_path, target)
    if not res["found"]:
        return None
    return {
        "text": res["matched_text"],
        "score": res["score"],
        "start": res["timestamp"],
        "end": res["end_timestamp"],
        "frame": res["frame"],
        "frame_num": res["frame_number"],
        "source": res["source"]
    }