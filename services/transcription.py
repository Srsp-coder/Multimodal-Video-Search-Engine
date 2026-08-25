import os
import subprocess
import tempfile
import whisper

_whisper_model = None


def get_whisper_model(model_name="base"):
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model(model_name)
    return _whisper_model


def transcribe_video(video_path):
    model = get_whisper_model()
    result = model.transcribe(
        video_path,
        word_timestamps=True,
        verbose=False
    )
    return result


def build_word_timeline(result):
    all_words = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            all_words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })
    return all_words


def verify_audio_window(video_path, target, candidate_start, candidate_end, window=5.0):
    """
    Transcribes a small window of audio around candidate timestamps to verify candidate match
    without performing full video transcription.
    """
    from services.dialogue_search import search_dialogue

    snippet_start = max(0.0, candidate_start - window)
    snippet_end = candidate_end + window
    duration = max(1.0, snippet_end - snippet_start)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_audio = os.path.join(temp_dir, "snippet.wav")
        command = [
            "ffmpeg",
            "-y",
            "-ss", str(snippet_start),
            "-i", video_path,
            "-t", str(duration),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            temp_audio
        ]

        res = subprocess.run(command, capture_output=True, text=True)
        if res.returncode != 0 or not os.path.exists(temp_audio):
            return None

        result = transcribe_video(temp_audio)
        words = build_word_timeline(result)
        if not words:
            return None

        # Adjust word timestamps relative to full video
        for w in words:
            w["start"] += snippet_start
            w["end"] += snippet_start

        match = search_dialogue(words, target)
        return match