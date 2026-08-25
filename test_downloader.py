from services.video_downloader import download_video


VIDEO_URL = "https://ok.ru/video/248244667877"


video_path = download_video(VIDEO_URL)

print()
print("===== DOWNLOAD RESULT =====")
print(f"Video : {video_path}")
print("============================")