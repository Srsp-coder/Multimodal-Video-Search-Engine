import whisper


model = whisper.load_model("base")


def transcribe_video(video_path):

    result = model.transcribe(
        video_path,
        word_timestamps=True,
        verbose=False
    )

    return result


def build_word_timeline(result):

    all_words = []

    for segment in result["segments"]:

        for word in segment.get("words", []):

            all_words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })

    return all_words