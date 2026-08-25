from services.transcription import (
    transcribe_video,
    build_word_timeline
)

from services.dialogue_search import (
    search_dialogue
)

from services.frame_extractor import (
    extract_frame
)


def process_video(video_path, target):

    # 1. Transcribe
    result = transcribe_video(video_path)

    # 2. Build continuous word timeline
    words = build_word_timeline(result)

    # 3. Search dialogue
    match = search_dialogue(
        words,
        target
    )

    if match is None:
        return None

    # 4. Extract frame
    frame, frame_num = extract_frame(
        video_path,
        match["start"]
    )

    return {
        **match,
        "frame": frame,
        "frame_num": frame_num
    }