import os
import yt_dlp


def download_video(url, output_dir="downloads"):

    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(
            output_dir,
            "%(id)s.%(ext)s"
        ),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "overwrites": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        video_id = info["id"]

        requested_downloads = info.get(
            "requested_downloads"
        )

        if requested_downloads:

            filepath = requested_downloads[0].get(
                "filepath"
            )

            if filepath and os.path.exists(filepath):
                return filepath

        # Fallback for merged mp4
        filepath = os.path.join(
            output_dir,
            f"{video_id}.mp4"
        )

        return filepath


def download_audio(url, output_dir="downloads"):

    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            output_dir,
            "%(id)s_audio.%(ext)s"
        ),
        "noplaylist": True,
        "overwrites": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        requested_downloads = info.get(
            "requested_downloads"
        )

        if requested_downloads:

            filepath = requested_downloads[0].get(
                "filepath"
            )

            if filepath and os.path.exists(filepath):
                return filepath

        ext = info.get("ext", "m4a")
        video_id = info.get("id", "audio")

        filepath = os.path.join(
            output_dir,
            f"{video_id}_audio.{ext}"
        )

        return filepath