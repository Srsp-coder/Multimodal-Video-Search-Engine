# Quest1 — Approach

## 1. Overview

Quest1 is a multi-modal video search engine that locates dialogue or visual text inside video streams and local files. Given a target text phrase and a video source, Quest1 searches through subtitles, audio, and visual frames to return:

- **found**: Whether the target was located (`true`/`false`)
- **source**: The search method that found the match (`subtitle`, `whisper`, or `ocr`)
- **matched_text**: The exact text snippet detected in the video
- **score**: Confidence score percentage
- **timestamp**: Formatted start timestamp (`H:MM:SS.sss`)
- **end_timestamp**: Formatted end timestamp (`H:MM:SS.sss`)
- **frame_number**: Corresponding video frame index
- **frame / frame_url**: Extracted image frame
- **video_path**: Source video path or URL

The system supports both **local video files** and **remote video URLs** (YouTube, HTTP/HTTPS links).

---

## 2. Search Strategy

Quest1 uses a cascading search priority designed to minimize processing time and bandwidth:

1. **Subtitle Search** (Fastest & Cheapest)
2. **Whisper / Audio Search** (Mid-tier)
3. **OCR / Visual Text Search** (Fallback)
4. **Frame Extraction** (Final Output)

### Key Optimization: Lazy Downloading

- **URL Input**: Subtitles are fetched without downloading the complete video.
- **Audio Processing**: Whisper uses audio-only streams/downloads without downloading full video files. Audio files are downloaded at most once and reused across verification and full Whisper search.
- **Full Video Download**: The complete video file is downloaded **only** when the search reaches the OCR stage.
- **Frame Extraction**: Frames are extracted directly from video streams or local files.

---

## 3. Complete Flow

```
                     Input
               (URL or Local File)
                        |
                        v
              Resolve Video Source
                        |
                        v
                 Search Subtitles
                        |
                   Match Found?
                    /        \
                  Yes         No
                   |           |
                   v           v
          Whisper Verification  Download Audio Only
                   |           |
               Verified?       v
                /    \      Whisper Search
              Yes     No       |
               |       |    Match Found?
               |       v     /       \
               |  Full Whisper  Yes    No
               |   Search      |       |
               |     |         |       v
               |  Match Found? |  Download Full Video
               |   /       \   |       |
               | Yes        No |       v
               |  |          \ |   OCR Search
               |  |           \|       |
               +--+------------+   Match Found?
                  |                 /        \
                  v               Yes         No
            Extract Frame          |          |
                  |                v          v
                  +----------> Result     Not Found
```

---

## 4. Subtitle → Audio Verification

- When a subtitle match is found, its timestamp is treated as an initial candidate region.
- A small audio window around the candidate timestamp (`candidate_start - 5s` to `candidate_end + 5s`) is extracted and verified using Whisper.
- If verification succeeds, Whisper's actual detected timestamps are returned as the result.
- If verification unconfirms the candidate match, the pipeline proceeds to a full Whisper audio search.

---

## 5. Audio Search

- When subtitle search finds no candidate (or verification fails), full audio is processed using OpenAI Whisper with word-level timestamps (`word_timestamps=True`).
- Dialogue search compares the target phrase against sliding word windows in the transcription timeline using RapidFuzz string matching.
- If a match exceeds the configured similarity threshold, its timestamps become the candidate result.

---

## 6. OCR Fallback

- OCR is reached **only** when both subtitle and audio searches fail to find the target.
- For URL inputs, the full video file is downloaded **only** when entering this stage.
- Video frames are sampled at intervals (`sample_interval = 0.5s`).
- OpenCV applies basic frame preprocessing (upscaling, grayscale conversion, and CLAHE contrast enhancement) to improve readability.
- EasyOCR extracts text from preprocessed frames, and matching scores are calculated using similarity metrics guarded against short-text false positives.

---

## 7. Final Result

- Once a candidate is located by Subtitle, Whisper, or OCR search:
  - The start and end timestamps are formatted into `H:MM:SS.sss` strings.
  - The corresponding video frame is extracted using OpenCV.
  - For web requests, the extracted frame is saved as a `.jpg` image in `results/` and exposed via URL (`/api/results/<filename>.jpg`).
  - The frontend displays real-time execution progress, result metadata, and the extracted image frame.

---

## 8. Current Architecture

```
Input / API Layer (FastAPI & CORS)
        ↓
Pipeline Orchestrator (pipeline.py)
        ↓
Subtitle Search  →  Whisper Audio  →  Visual OCR
        ↓
Frame Extractor (cv2.VideoCapture)
        ↓
React Frontend UI (Vite + SSE Streaming)
```

- **Backend**: FastAPI (`main.py`, `api/routes.py`, `api/schemas.py`) providing REST (`/api/search`) and real-time SSE streaming (`/api/search/stream`).
- **Frontend**: React + Vite UI (`frontend/`) providing real-time pipeline status logs, result cards, and image preview.

