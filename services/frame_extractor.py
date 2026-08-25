import cv2


def extract_frame(video_path, timestamp):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_num = int(timestamp * fps)

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_num
    )

    ret, frame = cap.read()

    cap.release()

    if not ret:
        raise RuntimeError(
            "Could not extract frame"
        )

    return frame, frame_num