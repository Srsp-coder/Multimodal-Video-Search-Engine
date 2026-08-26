import os
import cv2

from services.video_downloader import download_video, download_audio
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


def get_media_stream_url(url: str, format_spec: str = "bestaudio/best") -> str:
    """
    Helper to extract a direct media stream URL for remote URLs using yt-dlp.
    Returns the original URL if extraction fails or if url is a local path.
    """
    if not url.startswith(("http://", "https://")):
        return url
    try:
        import yt_dlp
        ydl_opts = {"format": format_spec, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url", url)
    except Exception as e:
        print(f"[PIPELINE] Stream URL resolution note: {e}")
        return url


def extract_frame_safe(source_or_url: str, timestamp: float):
    """
    Extracts frame from local path or stream URL.
    If stream extraction fails on a URL, falls back to downloading full video.
    """
    if not source_or_url.startswith(("http://", "https://")):
        return extract_frame(source_or_url, timestamp)

    try:
        stream_url = get_media_stream_url(source_or_url, "bestvideo/best")
        return extract_frame(stream_url, timestamp)
    except Exception as e:
        print(f"[PIPELINE] Stream frame extraction failed ({e}). Downloading video for frame extraction...")
        downloaded_path = download_video(source_or_url)
        return extract_frame(downloaded_path, timestamp)


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
    ocr_preprocess: bool = True,
    progress_callback = None
) -> dict:
    """
    Main orchestration pipeline for video dialogue & visual text search.
    Search priority: SUBTITLES -> WHISPER/AUDIO -> OCR -> FRAME EXTRACTION
    Lazy downloading: URLs use audio-only downloads for Whisper, full video only for OCR.
    """
    def log_progress(msg, stage=None, data=None):
        print(msg)
        if progress_callback:
            event = {"message": msg, "stage": stage or "status"}
            if data:
                event.update(data)
            progress_callback(event)

    log_progress(f"\n[PIPELINE] Resolving input source: '{source}'", stage="resolve")

    is_url = source.startswith(("http://", "https://"))

    if is_url:
        log_progress("[PIPELINE] Input type: URL", stage="resolve")
    else:
        log_progress("[PIPELINE] Input type: Local File", stage="resolve")
        if not os.path.exists(source):
            log_progress(f"[PIPELINE] Video file does not exist: {source}", stage="error")
            return make_empty_result(source, target)

        # Validate local video opening
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            log_progress(f"[PIPELINE] Video file exists but cannot be opened: {source}", stage="error")
            cap.release()
            return make_empty_result(source, target)
        cap.release()

    # Track audio path for remote URLs to ensure single audio-only download reused across Whisper steps
    audio_path = None

    def get_or_download_audio():
        nonlocal audio_path
        if not is_url:
            return source
        if audio_path is None or not os.path.exists(audio_path):
            log_progress("[PIPELINE] Downloading audio only for Whisper...", stage="audio_download")
            try:
                audio_path = download_audio(source)
                log_progress(f"[PIPELINE] Audio download complete: {audio_path}", stage="audio_download")
            except Exception as e:
                log_progress(f"[PIPELINE] Failed to download audio only: {e}", stage="audio_download_error")
                audio_path = None
        else:
            log_progress(f"[PIPELINE] Reusing downloaded audio for Whisper search: {audio_path}", stage="audio_download")
        return audio_path

    # 2. Subtitle Search
    if is_url:
        log_progress("[PIPELINE] Searching subtitles without downloading full video...", stage="subtitle")
    else:
        log_progress("[PIPELINE] Searching subtitles...", stage="subtitle")

    sub_match = None
    try:
        sub_match = search_video_subtitle(source, target, threshold=threshold)
    except Exception as e:
        log_progress(f"[PIPELINE] Subtitle search error (continuing): {e}", stage="subtitle")

    if sub_match is not None:
        candidate_start = sub_match["start"]
        candidate_end = sub_match["end"]
        formatted_start = format_timestamp(candidate_start)
        log_progress(
            f"[PIPELINE] Subtitle candidate found at {formatted_start} ({candidate_start:.2f}s, Score: {sub_match['score']:.1f})",
            stage="subtitle_candidate",
            data={"timestamp": formatted_start, "score": float(sub_match["score"])}
        )
        log_progress(f"[PIPELINE] Verifying candidate with Whisper ({verification_window}s window)...", stage="verify")

        local_audio = get_or_download_audio()
        v_match = None
        if local_audio is not None:
            try:
                v_match = verify_audio_window(
                    local_audio,
                    target,
                    candidate_start,
                    candidate_end,
                    window=verification_window
                )
            except Exception as e:
                log_progress(f"[PIPELINE] Candidate audio verification error: {e}", stage="verify")

        if v_match is not None:
            log_progress("[PIPELINE] Verification successful!", stage="verify_success")
            if is_url:
                log_progress("[PIPELINE] Full video download skipped.", stage="verify_success")

            final_start = v_match["start"]
            final_end = v_match["end"]
            frame, frame_num = extract_frame_safe(source, final_start)
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
                "video_path": source
            }
        else:
            log_progress("[PIPELINE] Verification unconfirmed. Proceeding to full Whisper search...", stage="verify_failed")
    else:
        log_progress("[PIPELINE] No matching subtitle found.", stage="subtitle_none")

    # 3. Whisper Audio Fallback
    log_progress("[PIPELINE] Executing full Whisper audio search...", stage="whisper")

    local_audio = get_or_download_audio()
    w_match = None
    if local_audio is not None:
        try:
            transcription_result = transcribe_video(local_audio)
            words = build_word_timeline(transcription_result)
            w_match = search_dialogue(words, target, threshold=threshold)
        except Exception as e:
            log_progress(f"[PIPELINE] Whisper search error (continuing): {e}", stage="whisper")

    if w_match is not None:
        formatted_start = format_timestamp(w_match["start"])
        log_progress(
            f"[PIPELINE] Whisper match found at {formatted_start} ({w_match['start']:.2f}s, Score: {w_match['score']:.1f})",
            stage="whisper_match",
            data={"timestamp": formatted_start, "score": float(w_match["score"])}
        )
        if is_url:
            log_progress("[PIPELINE] Full video download skipped.", stage="whisper_match")

        final_start = w_match["start"]
        final_end = w_match["end"]
        frame, frame_num = extract_frame_safe(source, final_start)
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
            "video_path": source
        }
    else:
        log_progress("[PIPELINE] Whisper audio search yielded no match.", stage="whisper_none")

    # 4. OCR Visual Fallback
    log_progress("[PIPELINE] No subtitle/audio match.", stage="ocr_init")
    log_progress("[PIPELINE] OCR fallback required.", stage="ocr_init")

    if is_url:
        log_progress("[PIPELINE] Downloading full video for OCR...", stage="ocr_download")
        try:
            downloaded_video_path = download_video(source)
            log_progress(f"[PIPELINE] Download complete: {downloaded_video_path}", stage="ocr_download")
        except Exception as e:
            log_progress(f"[PIPELINE] Failed to download video from URL for OCR: {e}", stage="error")
            return make_empty_result(source, target)
    else:
        downloaded_video_path = source

    if not os.path.exists(downloaded_video_path):
        log_progress(f"[PIPELINE] Video file does not exist for OCR: {downloaded_video_path}", stage="error")
        return make_empty_result(source, target)

    log_progress("[PIPELINE] Starting OCR...", stage="ocr")
    ocr_match = None
    try:
        ocr_match = search_frames(
            video_path=downloaded_video_path,
            target=target,
            sample_interval=ocr_sample_interval,
            threshold=threshold,
            preprocess=ocr_preprocess,
            fine_refine=True
        )
    except Exception as e:
        log_progress(f"[PIPELINE] OCR search error: {e}", stage="ocr")

    if ocr_match is not None:
        timestamp = ocr_match["timestamp"]
        formatted_start = format_timestamp(timestamp)
        log_progress(
            f"[PIPELINE] OCR match found at {formatted_start} ({timestamp:.2f}s, Score: {ocr_match['score']:.1f})",
            stage="ocr_match",
            data={"timestamp": formatted_start, "score": float(ocr_match["score"])}
        )
        frame, frame_num = extract_frame(downloaded_video_path, timestamp)
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
            "video_path": downloaded_video_path
        }

    log_progress("[PIPELINE] Target search completed: Not found in subtitles, audio, or visual frames.", stage="complete")
    return make_empty_result(source, target)


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