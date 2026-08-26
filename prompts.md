# Development Prompts & Changes
## 1 - Research on Tech Stack
### Prompt
> This is the given PS pdf, My understanding is that we have to transcribe the given video, save it as text & search the given dialogue in it, then return the starting time stamp of the dialogue & the corresponding frame of it too. What kind of tech stack may i use? Detail on why it is chosen & remember the key steps- transcribe, search, return timestamp, return frame.
### Outcome
#### Recommended Tech Stack
| Library | Purpose |
|---|---|
| **yt-dlp** | Audio/Video Downloader |
| **Whisper** | transcribtion |
| **ffmpeg** | Audio/Video Decoding |
| **OpenCV** |  Extract Video Frame |
| **RapidFuzz** |  Fuzzy text Matching |

### My Work
- Researched on them individually
- Decided to test them all with a small code block

## 2 - Test Code (Commit Hash - c184656bf6f7f184a406f43fe6569f5a4dd2fd89)
### Prompt
> Give a test code using all these stack, A small understandable python code file
### Outcome
- Gave code, which I pasted in test.py
### My work
- Installed ffmpeg, added file path in the system variables
- Ran the code, it took some time to download the video
- It returned the exact timestamp & Frame of the given sample dialogue in the sample video
- Decided to test with many videos. For now removed the download video Step as it is taking more time

> Removed the download Video Logic (Commit Hash - 33d6e3127b365f3bf82d0bdb3a17593ea9090285)

### 3 - Segment-level to Word-level fuzzy search (Commit Hash - e98aa884dc20db9afdd8f9f9eab3aa2c033a87b2)
- When tested the previous code with other video from YouTube, it failed when prompted few dialogues. Tried debugging by printing the variables at every step, found that it just used the segments, not the word timestamp dictionary. Gave the response to AI & typed the following prompt.
### Prompt
> Failed for this case, how may I improve the code?
### Outcome
- Updated the word level fuzzy matching with sliding window logic
### My work
- When tested, it failed at few cases like when the phrase is spread across different segments

### 4 - Updated to Segment Combination Search (Commit Hash - fac9ad2d4e38204efd03d308286e6178908bdf22)
### Prompt
> Failed for this case where the words are spread across two different segment, how may I improve the code?
### Outcome
- Added a list which has all words & their start, end timestamps in it
### My Work
- Tested, Worked properly for many videos

### 5 - Service Division(Commit Hash - 7fb9092b28a994f39a3a957984949ac3d7a1c5a6)
### Prompt
> we must also see the frames and look for text, let's do that first and check. Then we will continue with this structured approach. Want all things as separate services in python now. Like download video, transcript, dialogue search(text), dialogue search(frame), frame extractor. First suggest whether am I crct in terms of these services
> Frame by frame search is time consuming right? So why not we search first the audio( already done), then subtitles, then frame by frame ocr? If wrong suggest a better optimal order
> Gave Code For now divide these into services. Rest all we'll do next(like the ocr & subtitle thing, download)

### Outcome
- Divided the test.py to services- dialogue_search, framee_extraction, transcription. Added pipeline.py
### My Work
- Tested the pipeline once, deleted the test.py

### 6 - Added Subtitle, OCR, Video Download services(Commit Hash - abc65ca3fa46db7d65ad816d3cc74741dcdb48bc)
### Prompt
> Now give the code for the rest all services(Downloader, Visual Path, Subtitles), lets test them only separately first. Then after confirmiung let us integrate it in our current pipeline
> Pasted Output of subtitles have some time difference, check where it went wrong
### Outcome
- Gave code files, tested them
### My Work
- Decided to connect all of them into a single pipeline

### 7 - Signle Pipeline(Commit Hash - 9a2f8481132d2250eafc1e8e1b128ff66aa4a75e)
### Prompt
> I need a proper pipeline.py code which utilises all these services.
> Doubts-Whats the pipeline? My idea- First check subtitles- if not there, use audio. If found search and find time stamp and for verification, search in that timestamp window using audio. If wrong, just do full audio search. If correct, just find the most appropriate starting timestamp and frame,
> How will the structure might change if we are going to have fastapi?
### Prompt 2
> can you give like a antigravity prompt, which does all change u had saidd, and does the proper pipeline.py. Make sure it doesnt change the current behavior and make it complex. The changes must be only related to the desired pipeline. Give the perfect prompt highlighting these

### Outcome 
- Created a pipeline

### My work
- Tested, did few changes

### 8 - FastAPI Layer(Commit Hash - 47ce13ace3328e23894969c5d1114e31e8eb61e8)
### Prompt
> Give antigravity prompt to build this fastapi thing. Make sure no changes are made to any of these services's logic.
### Outcome
- Created api/, rotes.py, schemas.py, Edited main.py
### My work
- Identified that the timestamp is not returned in the expected format
- Also subtitle -> Audio fallback logic had few issues

### 9 -  Timestamp correction, SUbtitle fallback
### Prompt 1
> Update the existing pipeline.py to format the returned `timestamp` and `end_timestamp` values as `H:MM:SS.sss` (e.g., `0:12:31.600`) instead of raw seconds.
> Requirements:
> - Make ONLY this timestamp-formatting change.
> - Add a small helper function for converting seconds to `H:MM:SS.sss`.
> - Apply it to subtitle, Whisper, and OCR results.
> - Keep `None` unchanged for not-found results.
> - Do NOT modify any search logic, thresholds, service calls, return structure, or pipeline behavior.
> - Preserve all existing keys and output structure exactly.
> - Do not modify any other files.

### Prompt 2
> Fix the subtitle → Whisper verification logic ONLY. Do not modify unrelated pipeline behavior.
> EXPECTED EXACT WORKFLOW:
> 1. Search subtitles for the target dialogue.
> 2. If NO subtitle match is found:
> → perform the existing FULL Whisper search over the entire video.
> 3. If a subtitle match IS found:
>    - Suppose subtitle match is:
>        start = 45.0s
>        end   = 47.0s
>    - Whisper verification must transcribe ONLY the audio window:
>        40.0s → 52.0s
>      i.e. candidate_start - 5 seconds through candidate_end + 5 seconds.
>    - Whisper must search for the target ONLY within this extracted verification audio.
>    - If Whisper finds the target, return Whisper's ACTUAL detected start/end timestamps converted back to absolute video timestamps.
>    - Do NOT return the subtitle timestamp as the Whisper timestamp.
>    - Do NOT allow Whisper to search outside this ±5 second verification window.
> 4. If Whisper verification does NOT find the target inside that window:
>    → perform the existing FULL Whisper search over the entire video.
> 5. If the full Whisper search also fails:
>    → continue to the existing OCR fallback.
> IMPORTANT:
> - The ±5 second window is relative to the subtitle match:
>     snippet_start = max(0, candidate_start - 5)
>     snippet_end   = candidate_end + 5
> - Whisper timestamps from the temporary audio file are relative to that audio file, so convert them back to absolute video timestamps by adding snippet_start.
> - The returned timestamp must represent the ACTUAL Whisper word match, not the beginning of the verification window.
> - Preserve the existing search_dialogue() behavior unless absolutely necessary.
> - Do NOT change pipeline.py.
> - Do NOT change the return structure.
> - Do NOT change timestamp formatting.
> - Do NOT change the full Whisper fallback behavior.
> - Do NOT change OCR behavior.
> - Make the smallest possible change required to implement this exact flow.
> CRITICAL BUG TO FIX:
> If the subtitle match is around 109.75s and Whisper detects the target at 106.73s, this should be accepted ONLY if 106.73s is genuinely the target speech inside the intended 5-second verification window. Do not simply force the result to 109.75s. The goal is accurate Whisper timing within the subtitle-derived window.
