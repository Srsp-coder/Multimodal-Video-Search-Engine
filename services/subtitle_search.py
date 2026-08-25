import os
import json
import glob
import subprocess
import tempfile
import re

from rapidfuzz import fuzz


# ============================================================
# 1. LOCAL VIDEO: FIND SUBTITLE STREAMS
# ============================================================

def get_subtitle_streams(video_path):

    command = [
        "ffprobe",
        "-v", "quiet",
        "-select_streams", "s",
        "-show_entries",
        "stream=index,codec_name:stream_tags=language,title",
        "-of", "json",
        video_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffprobe failed:\n{result.stderr}"
        )

    data = json.loads(result.stdout)

    return data.get("streams", [])


# ============================================================
# 2. CHOOSE ENGLISH SUBTITLE
# ============================================================

def choose_english_subtitle(streams):

    # First preference: English
    for stream in streams:

        tags = stream.get("tags", {})

        language = tags.get("language", "").lower()

        if language in ["eng", "en"]:
            return stream

    # Second preference: subtitle title contains English
    for stream in streams:

        tags = stream.get("tags", {})

        title = tags.get("title", "").lower()

        if "english" in title:
            return stream

    # Fallback: first subtitle stream
    return streams[0]


# ============================================================
# 3. LOCAL VIDEO: EXTRACT SUBTITLE
# ============================================================

def extract_subtitle(video_path, stream_index, output_path):

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-map", f"0:{stream_index}",
        "-c:s", "srt",
        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Subtitle extraction failed:\n{result.stderr}"
        )

    return output_path


# ============================================================
# 4. URL: DOWNLOAD ONLY SUBTITLES
# ============================================================

def download_subtitle_from_url(url, output_dir):

    command = [
    "yt-dlp",

    "--skip-download",

    "--write-subs",
    "--write-auto-subs",

    "--sub-langs", "en-US",

    "--sub-format", "vtt",

    "-o",
    os.path.join(
        output_dir,
        "%(id)s.%(ext)s"
    ),

    url
]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Subtitle download failed:\n{result.stderr}"
        )

    subtitle_files = sorted(
        glob.glob(
            os.path.join(output_dir, "*.vtt")
        )
    )

    if not subtitle_files:
        return None

    return subtitle_files[0]


# ============================================================
# 5. PARSE SUBTITLE TIMESTAMP
# ============================================================

def parse_subtitle_time(time_string):

    time_string = time_string.strip()

    # Remove VTT settings
    time_string = time_string.split()[0]

    # VTT uses .
    # SRT uses ,
    if "." in time_string:

        hours, minutes, seconds = time_string.split(":")

        seconds, milliseconds = seconds.split(".")

    else:

        hours, minutes, seconds = time_string.split(":")

        seconds, milliseconds = seconds.split(",")

    # Make sure milliseconds are exactly 3 digits
    milliseconds = milliseconds.ljust(3, "0")[:3]

    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


# ============================================================
# 6. CLEAN SUBTITLE TEXT
# ============================================================

def clean_subtitle_text(text):

    # Remove HTML/VTT tags
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    # Remove VTT positioning tags
    text = re.sub(
        r"\{[^}]+\}",
        "",
        text
    )

    # Normalize whitespace
    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# 7. PARSE SUBTITLE FILE
# ============================================================

def parse_subtitle_file(subtitle_path):

    with open(
        subtitle_path,
        "r",
        encoding="utf-8-sig"
    ) as file:

        content = file.read()

    # Normalize line endings
    content = content.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    blocks = re.split(
        r"\n\s*\n",
        content.strip()
    )

    entries = []

    for block in blocks:

        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        timestamp_index = None

        for i, line in enumerate(lines):

            if "-->" in line:

                timestamp_index = i
                break

        if timestamp_index is None:
            continue

        timestamp_line = lines[timestamp_index]

        try:

            start_time, end_time = (
                timestamp_line.split(
                    "-->",
                    1
                )
            )

            start = parse_subtitle_time(
                start_time
            )

            end = parse_subtitle_time(
                end_time
            )

        except ValueError:
            continue

        text = " ".join(
            lines[timestamp_index + 1:]
        )

        text = clean_subtitle_text(
            text
        )

        if not text:
            continue

        entries.append({
            "text": text,
            "start": start,
            "end": end
        })

    return entries


# ============================================================
# 8. CALCULATE MATCH SCORE
# ============================================================

def calculate_score(target, text):

    target = target.lower().strip()
    text = text.lower().strip()

    partial_score = fuzz.partial_ratio(
        target,
        text
    )

    ratio_score = fuzz.ratio(
        target,
        text
    )

    token_score = fuzz.token_set_ratio(
        target,
        text
    )

    # Weighted score
    score = (
        partial_score * 0.5
        + ratio_score * 0.2
        + token_score * 0.3
    )

    return score


# ============================================================
# 9. SEARCH SUBTITLE USING SLIDING WINDOWS
# ============================================================

def search_subtitle(
    subtitle_path,
    target,
    threshold=70,
    window_sizes=(1, 2, 3)
):

    entries = parse_subtitle_file(
        subtitle_path
    )

    if not entries:
        return None

    target_clean = clean_subtitle_text(
        target
    ).lower()

    best_match = None
    best_score = 0

    # --------------------------------------------------------
    # Sliding subtitle windows
    # --------------------------------------------------------

    for window_size in window_sizes:

        for i in range(
            len(entries) - window_size + 1
        ):

            window = entries[
                i:i + window_size
            ]

            combined_text = " ".join(
                entry["text"]
                for entry in window
            )

            score = calculate_score(
                target_clean,
                combined_text
            )

            if score > best_score:

                best_score = score

                best_match = {
                    "text": combined_text,
                    "score": score,
                    "start": window[0]["start"],
                    "end": window[-1]["end"],
                    "window_size": window_size
                }

    # --------------------------------------------------------
    # Apply threshold AFTER searching everything
    # --------------------------------------------------------

    if best_match is not None:

        if best_match["score"] >= threshold:
            return best_match

    return None


# ============================================================
# 10. MAIN FUNCTION
# ============================================================

def search_video_subtitle(
    source,
    target,
    threshold=70
):

    # ========================================================
    # CASE 1: URL
    # ========================================================

    if source.startswith(
        ("http://", "https://")
    ):

        print("Source: URL")
        print("Downloading subtitles only...")

        with tempfile.TemporaryDirectory() as temp_dir:

            subtitle_path = (
                download_subtitle_from_url(
                    source,
                    temp_dir
                )
            )

            if subtitle_path is None:

                print(
                    "No English subtitles found."
                )

                return None

            print(
                f"Subtitle: "
                f"{os.path.basename(subtitle_path)}"
            )

            return search_subtitle(
                subtitle_path,
                target,
                threshold
            )

    # ========================================================
    # CASE 2: LOCAL VIDEO
    # ========================================================

    else:

        print("Source: Local video")

        streams = get_subtitle_streams(
            source
        )

        if not streams:

            print(
                "No subtitle streams found."
            )

            return None

        print(
            f"Found {len(streams)} "
            f"subtitle stream(s)."
        )

        # Choose English subtitle
        selected_stream = (
            choose_english_subtitle(
                streams
            )
        )

        stream_index = (
            selected_stream["index"]
        )

        tags = selected_stream.get(
            "tags",
            {}
        )

        print(
            f"Selected subtitle stream: "
            f"{stream_index}"
        )

        print(
            f"Language: "
            f"{tags.get('language', 'unknown')}"
        )

        print(
            f"Title: "
            f"{tags.get('title', 'unknown')}"
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            subtitle_path = os.path.join(
                temp_dir,
                "subtitle.srt"
            )

            extract_subtitle(
                source,
                stream_index,
                subtitle_path
            )

            return search_subtitle(
                subtitle_path,
                target,
                threshold
            )


# ============================================================
# 11. EXAMPLE
# ============================================================

if __name__ == "__main__":

    source = "https://youtu.be/NdvqHc56lE0"

    # Or local video:
    # source = "video.mp4"

    target = "We plan to strike"

    result = search_video_subtitle(
        source,
        target,
        threshold=70
    )

    if result:

        print("\nMATCH FOUND!")

        print(
            f"Text        : {result['text']}"
        )

        print(
            f"Score       : {result['score']:.2f}"
        )

        print(
            f"Start       : {result['start']:.3f}s"
        )

        print(
            f"End         : {result['end']:.3f}s"
        )

        print(
            f"Window size : {result['window_size']}"
        )

    else:

        print(
            "\nNo matching subtitle found."
        )