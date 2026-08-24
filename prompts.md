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
