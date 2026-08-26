# Quest1 - Video Dialogue & Text Search Engine

Quest1 is an intelligent multi-modal video search engine that locates target dialogue or visual text inside video streams and local video files. It pinpoints the exact timestamp (`H:MM:SS.sss`), confidence score, matched text snippet, and extracts the corresponding image frame.

---

## 🚀 Features

1. **Multi-Modal Cascading Search**:
   - **Subtitles First (Fastest)**: Uses `yt-dlp` to fetch subtitles (`.vtt`) or embedded `.srt`/`.vtt` streams without downloading full video files.
   - **Audio Verification & Whisper Fallback**: Downloads audio-only tracks for Whisper candidate verification and full audio search. Reuses downloaded audio across verification and full Whisper search.
   - **OCR Visual Fallback**: Downloads full video **only** if subtitle and audio searches fail, running EasyOCR with OpenCV frame preprocessing (upscaling, grayscale, CLAHE contrast enhancement).
2. **Lazy Downloading**: Remote video URLs (`http://`/`https://`) do not download full video files unless OCR is actually required.
3. **Formatted Timestamps**: Timestamps are formatted as `H:MM:SS.sss` (e.g. `0:12:31.600`).
4. **FastAPI & Real-time Progress Streaming**: Exposes REST and Server-Sent Events (SSE) endpoints streaming live progress updates (`✓ completed`, `● running`, `○ pending`).
5. **Modern React Frontend**: A React + Vite UI featuring real-time processing log timeline, confidence badges, formatted timestamp output, and extracted JPG frame previews.

---

## 🛠️ Project Architecture

```
Quest1/
├── api/
│   ├── routes.py            # FastAPI endpoints (/api/search, /api/search/stream)
│   └── schemas.py           # Pydantic SearchResponse data models
├── services/
│   ├── video_downloader.py  # yt-dlp video and audio-only downloader
│   ├── subtitle_search.py   # Subtitle extraction & sliding window fuzzy search
│   ├── transcription.py     # Whisper transcription & audio window verification
│   ├── dialogue_search.py   # Word timeline dialogue fuzzy matching (RapidFuzz)
│   ├── frame_text_search.py # EasyOCR visual text search & OpenCV preprocessing
│   └── frame_extractor.py   # OpenCV frame extraction by timestamp/stream URL
├── frontend/                # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx          # Search Form, Live SSE Log Timeline, Result Cards
│   │   └── App.css          # Developer-tool styling
│   └── package.json
├── pipeline.py              # Main search pipeline orchestration & stream helpers
├── main.py                  # FastAPI app entry point & CLI runner mode
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 📋 Prerequisites & Installation

### 1. System Requirements
- **Python**: `3.9` or higher (Python 3.10+ recommended)
- **Node.js**: `v18` or higher and `npm`
- **FFmpeg**: Must be installed and available in system `PATH` (used for audio snippet extraction and media probing).

### 2. Python Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

> **Note on FFmpeg**: Ensure `ffmpeg` and `ffprobe` are in your system `PATH`. On Windows, you can install via `winget install FFmpeg` or download from official builds.

### 3. React Frontend Setup

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

---

## 🏃 How to Run the Solution

### Option 1: Run Web Application (FastAPI + React)

#### Step 1: Start the FastAPI Backend
In the project root directory, run:

```bash
uvicorn main:app --reload
```
The FastAPI backend starts at `http://127.0.0.1:8000`.
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

#### Step 2: Start the React Frontend
In a separate terminal window, navigate to the `frontend` directory and run:

```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

### Option 2: Run via Command Line Interface (CLI)

Run the pipeline directly via Python CLI mode:

```bash
python main.py
```

Or execute custom search queries in Python code:

```python
from pipeline import search_video

result = search_video(
    source="https://youtu.be/NdvqHc56lE0",  # Remote URL or local file path ("video5.mp4")
    target="crossed 50 yrs"
)

if result["found"]:
    print(f"Source Method : {result['source']}")
    print(f"Matched Text  : {result['matched_text']}")
    print(f"Score         : {result['score']:.2f}%")
    print(f"Start Time    : {result['timestamp']}")
    print(f"End Time      : {result['end_timestamp']}")
    print(f"Frame Number  : {result['frame_number']}")
```

---

## 🌐 API Reference

### `POST /api/search`
Standard endpoint returning full JSON search response. Accepts `multipart/form-data`:

- `target` (string, required): Dialogue or text to locate.
- `url` (string, optional): Remote video URL (YouTube, direct HTTP/HTTPS link, etc.).
- `video` (file, optional): Uploaded local video file.

**Sample Response:**
```json
{
  "found": true,
  "source": "whisper",
  "target": "crossed 50 yrs",
  "matched_text": "crossed 50 yrs old",
  "score": 92.5,
  "timestamp": "0:12:31.600",
  "end_timestamp": "0:12:35.100",
  "frame_number": 1808,
  "video_path": "https://youtu.be/NdvqHc56lE0",
  "frame_url": "/api/results/a1b2c3d4.jpg"
}
```

### `POST /api/search/stream`
Server-Sent Events (SSE) streaming endpoint returning real-time progress events (`data: {...}\n\n`) followed by the final result payload.

---

## 🧪 Pipeline Search Priority Rules

1. **Subtitles First**: Subtitles are extracted/downloaded without downloading the video file.
2. **Whisper Audio Search**: Audio-only tracks (`.m4a`/`.webm`) are downloaded for Whisper transcription & dialogue fuzzy matching.
3. **Lazy Video Downloading**: Full video files are downloaded **only** if subtitle and audio searches fail and OCR fallback is triggered.
4. **Result Frame**: Extracted frames are stored in `results/` and exposed via static URL `/api/results/<filename>.jpg`.
