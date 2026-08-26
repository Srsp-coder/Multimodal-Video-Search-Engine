**==========================**

**Step 7 - Pipeline Prompt**

**==========================**

You are modifying my existing Quest1 project.



IMPORTANT:

Do NOT redesign the project from scratch.

Do NOT replace working implementations unnecessarily.

Do NOT change existing behavior unless it is required to implement the pipeline described below.

Make only the changes required for the desired search pipeline and clean service integration.



The project already contains working services for:



\- subtitle search

\- Whisper transcription

\- dialogue search

\- frame extraction

\- OCR/frame text search

\- URL/video downloading



I have provided the current implementations in the project.



============================================================

&#x20;                   PRIMARY GOAL

============================================================



Build a robust central `pipeline.py` that orchestrates the

existing services into a single intelligent video-search

pipeline.



The input can be either:



1\. A local video file

2\. A URL supported by yt-dlp



The user provides:



\- video source

\- target dialogue/text



The system must locate the most appropriate timestamp and

corresponding video frame containing that target.



The pipeline must use the following search priority:



&#x20;   SUBTITLES

&#x20;       ↓

&#x20;   WHISPER / AUDIO

&#x20;       ↓

&#x20;   OCR

&#x20;       ↓

&#x20;   final frame extraction



Do NOT run all three unnecessarily.



============================================================

&#x20;                REQUIRED SEARCH PIPELINE

============================================================



Implement this overall flow:



&#x20;                   INPUT

&#x20;                URL or FILE

&#x20;                    |

&#x20;                    v

&#x20;             Resolve Input

&#x20;                    |

&#x20;            +-------+-------+

&#x20;            |               |

&#x20;           URL            FILE

&#x20;            |               |

&#x20;            v               |

&#x20;      Download Video        |

&#x20;            |               |

&#x20;            +-------+-------+

&#x20;                    |

&#x20;                    v

&#x20;            SUBTITLE SEARCH

&#x20;                    |

&#x20;            +-------+-------+

&#x20;            |               |

&#x20;          FOUND           NOT FOUND

&#x20;            |               |

&#x20;            |               v

&#x20;            |          WHISPER SEARCH

&#x20;            |               |

&#x20;            |        +------+------+

&#x20;            |        |             |

&#x20;            |      FOUND         NOT FOUND

&#x20;            |        |             |

&#x20;            |        |             v

&#x20;            |        |            OCR

&#x20;            |        |             |

&#x20;            |        |       +-----+-----+

&#x20;            |        |       |           |

&#x20;            |        |     FOUND       NOT FOUND

&#x20;            |        |       |           |

&#x20;            +--------+-------+-----------+

&#x20;                     |

&#x20;                     v

&#x20;             Candidate Timestamp

&#x20;                     |

&#x20;                     v

&#x20;            Verification / Refinement

&#x20;                     |

&#x20;                     v

&#x20;            Best Starting Timestamp

&#x20;                     |

&#x20;                     v

&#x20;              Extract Frame

&#x20;                     |

&#x20;                     v

&#x20;                 RESULT





============================================================

&#x20;             INPUT HANDLING REQUIREMENTS

============================================================



The pipeline must accept either a URL or a local video path.



Determine whether the input is a URL or local file.



For a URL:



&#x20;   URL

&#x20;     ↓

&#x20;   existing download\_video()

&#x20;     ↓

&#x20;   local video path



For a local file:



&#x20;   use the file directly



Do NOT duplicate yt-dlp functionality inside pipeline.py.



Use the existing `download\_video()` service.



Validate that the resolved video actually exists and can be

opened before starting expensive processing.



Do not modify the downloader's fundamental behavior.



============================================================

&#x20;                SUBTITLE-FIRST BEHAVIOR

============================================================



Subtitle search must always be attempted first.



If subtitles are available:



&#x20;   search the target in the subtitle timeline.



If the target is found reliably:



&#x20;   use the subtitle result as the initial candidate.



Do NOT immediately run full Whisper transcription if the

subtitle result is already strong.



The goal is to make subtitle search the cheapest and fastest

path.



If subtitles are unavailable or the target is not found:



&#x20;   fall back to Whisper.



Do not break the existing subtitle service.



Adapt its output to the pipeline if necessary rather than

rewriting it unnecessarily.



============================================================

&#x20;                WHISPER SEARCH BEHAVIOR

============================================================



Use the existing Whisper transcription service.



The existing service provides word-level timestamps.



Use:



&#x20;   transcribe\_video()



and:



&#x20;   build\_word\_timeline()



Then use:



&#x20;   search\_dialogue()



for target matching.



Do not duplicate Whisper transcription logic inside

pipeline.py.



The pipeline should orchestrate the service.



============================================================

&#x20;            IMPORTANT WHISPER VERIFICATION LOGIC

============================================================



If subtitle search finds a candidate timestamp, do NOT blindly

trust it.



The candidate should be verified using the audio/Whisper

timeline around that timestamp.



Conceptually:



&#x20;   subtitle match

&#x20;         ↓

&#x20;   candidate timestamp

&#x20;         ↓

&#x20;   search/verify nearby audio window

&#x20;         ↓

&#x20;   correct?

&#x20;      /     \\

&#x20;    YES      NO

&#x20;     |        |

&#x20;     |        v

&#x20;     |    full Whisper search

&#x20;     |        |

&#x20;     +--------+

&#x20;          |

&#x20;          v

&#x20;     best timestamp



The verification window should be configurable.



For example:



&#x20;   verification\_window = 5 seconds



Do not hardcode the value throughout the code.



Put pipeline parameters in one configuration section or use

function arguments.



If the target is verified in the nearby audio window:



&#x20;   keep the candidate.



If it is not verified:



&#x20;   perform the full Whisper search.



This avoids unnecessarily transcribing/searching everything

when subtitles are already accurate.



============================================================

&#x20;             FULL AUDIO FALLBACK

============================================================



If subtitle search fails completely:



&#x20;   perform full Whisper transcription/search.



If subtitle candidate verification fails:



&#x20;   perform full Whisper search.



If Whisper finds the target:



&#x20;   use the Whisper result as the candidate.



If Whisper cannot find the target reliably:



&#x20;   trigger OCR.



The OCR fallback must only happen after subtitle/audio

search fails.



============================================================

&#x20;                      OCR FALLBACK

============================================================



OCR is the final fallback.



Use the existing:



&#x20;   frame\_text\_search.py



service.



Do not make OCR run before subtitles or Whisper.



OCR should search the video visually for the target.



The OCR service should support preprocessing/upscaling for

low-quality videos.



The existing EasyOCR implementation should remain the OCR

engine for now.



Do NOT introduce PaddleOCR.



Do NOT add PaddleOCR dependencies.



Do NOT attempt to fix or integrate the current PaddleOCR

installation.



The current Quest1 OCR direction is EasyOCR + preprocessing.



============================================================

&#x20;                LOW-QUALITY VIDEO OCR

============================================================



The OCR service should be improved only as required for this

pipeline.



For low-quality videos, especially 144p, use preprocessing

before EasyOCR.



At minimum support:



&#x20;   - upscaling

&#x20;   - grayscale conversion

&#x20;   - contrast enhancement

&#x20;   - OCR after preprocessing



Use OpenCV for preprocessing.



Do NOT claim that upscaling can reconstruct information that

does not exist.



The goal is to make existing text more OCR-readable.



The OCR matching logic MUST NOT allow tiny accidental OCR

results to become false positives.



For example:



&#x20;   Target:

&#x20;       "In my younger age"



&#x20;   OCR:

&#x20;       "M"



must NEVER become a 100% match.



Avoid relying solely on `fuzz.partial\_ratio()`.



Use robust matching based on normalized text and multiple

similarity measures where appropriate.



Require sufficient textual overlap/word count for multi-word

targets.



============================================================

&#x20;            OCR SEARCH EFFICIENCY REQUIREMENT

============================================================



Do NOT blindly OCR every frame.



The OCR search should use configurable sampling.



For example:



&#x20;   coarse interval = 0.5 seconds



But keep the interval configurable.



Do not hardcode it everywhere.



If appropriate, implement a two-stage OCR search:



&#x20;   coarse search

&#x20;         ↓

&#x20;   promising region

&#x20;         ↓

&#x20;   fine search

&#x20;         ↓

&#x20;   best OCR candidate



However, keep this implementation modular and do not turn

pipeline.py into an OCR implementation.



OCR logic belongs in the OCR service.



============================================================

&#x20;             TIMESTAMP REFINEMENT

============================================================



Once a candidate is found, the pipeline must determine the

most appropriate starting timestamp.



Do NOT simply return the timestamp of the first coarse search

sample.



For example:



&#x20;   OCR sample:

&#x20;       22.00s



does NOT automatically mean:



&#x20;   final timestamp = 22.00s



The target may actually appear at:



&#x20;   21.63s



Similarly, a Whisper/subtitle result may represent a dialogue

range.



The pipeline should preserve:



&#x20;   start

&#x20;   end



when available.



The final timestamp should represent the most appropriate

START of the target occurrence.



Use the most accurate timestamp source available:



&#x20;   Whisper word timestamp

&#x20;       >

&#x20;   subtitle timestamp

&#x20;       >

&#x20;   OCR sampled timestamp



when such precision is available.



If OCR is the only source, refine around the best OCR

candidate when practical.



============================================================

&#x20;                  FRAME EXTRACTION

============================================================



Once the final timestamp is determined, use the existing:



&#x20;   extract\_frame()



service.



Do NOT duplicate OpenCV frame extraction logic inside

pipeline.py.



The result must include:



&#x20;   timestamp

&#x20;   frame number

&#x20;   extracted frame



The pipeline should not assume that the frame number exists

inside an OCR result unless the OCR service actually returns

it.



Fix any mismatch between service return structures and the

pipeline.



============================================================

&#x20;                 RESULT STRUCTURE

============================================================



Create one consistent result structure returned by the

pipeline.



For example:



{

&#x20;   "found": True,

&#x20;   "source": "subtitle" | "whisper" | "ocr",

&#x20;   "target": "...",

&#x20;   "matched\_text": "...",

&#x20;   "score": 92.5,

&#x20;   "timestamp": 21.63,

&#x20;   "frame\_number": 648,

&#x20;   "frame": <OpenCV frame>,

&#x20;   "video\_path": "..."

}



If not found:



{

&#x20;   "found": False,

&#x20;   "target": "...",

&#x20;   "source": None,

&#x20;   "matched\_text": None,

&#x20;   "score": 0,

&#x20;   "timestamp": None,

&#x20;   "frame\_number": None,

&#x20;   "frame": None,

&#x20;   "video\_path": "..."

}



The exact structure can be adjusted to fit the existing

project conventions, but it must be consistent across all

three search methods.



Do NOT return completely different structures depending on

which service found the target.



============================================================

&#x20;                   SERVICE BOUNDARIES

============================================================



Maintain clear responsibilities.



`pipeline.py`

&#x20;   Orchestrates everything.



`download\_video()`

&#x20;   URL → local video.



`subtitle service`

&#x20;   Subtitle retrieval/search.



`whisper service`

&#x20;   Audio transcription + word timeline.



`dialogue\_search`

&#x20;   Search target in word timeline.



`frame\_text\_search`

&#x20;   OCR visual search.



`extract\_frame`

&#x20;   Timestamp → video frame.



Do NOT move all logic into pipeline.py.



Do NOT duplicate service implementations.



============================================================

&#x20;                MODEL INITIALIZATION

============================================================



Do not repeatedly initialize expensive models.



Especially:



&#x20;   EasyOCR Reader

&#x20;   Whisper model



Use module-level lazy initialization or another safe reusable

approach consistent with the current project.



The first request may initialize the model.



Subsequent searches should reuse it.



Do not load the OCR model once per frame.



Do not load Whisper once per word/window.



============================================================

&#x20;                   ERROR HANDLING

============================================================



The pipeline must fail gracefully.



Handle:



&#x20;   - invalid URL

&#x20;   - failed download

&#x20;   - missing video

&#x20;   - unreadable video

&#x20;   - unavailable subtitles

&#x20;   - subtitle parsing failure

&#x20;   - Whisper failure

&#x20;   - OCR failure

&#x20;   - frame extraction failure



A failure in subtitle processing should NOT automatically

terminate the entire pipeline.



For example:



&#x20;   subtitle error

&#x20;       ↓

&#x20;   continue to Whisper



Likewise:



&#x20;   Whisper failure/no result

&#x20;       ↓

&#x20;   continue to OCR



Only return an error when the pipeline genuinely cannot

process the input.



============================================================

&#x20;                LOGGING / DEBUG OUTPUT

============================================================



Keep useful console logging because this is currently being

developed and tested from the terminal.



Clearly show:



&#x20;   INPUT

&#x20;   SUBTITLE SEARCH

&#x20;   WHISPER SEARCH

&#x20;   VERIFICATION

&#x20;   OCR FALLBACK

&#x20;   FINAL RESULT



Example:



&#x20;   \[PIPELINE] Resolving input...

&#x20;   \[PIPELINE] Input type: URL

&#x20;   \[PIPELINE] Download complete.

&#x20;   \[PIPELINE] Searching subtitles...

&#x20;   \[PIPELINE] Subtitle candidate: 21.40s

&#x20;   \[PIPELINE] Verifying candidate with Whisper...

&#x20;   \[PIPELINE] Verification successful.

&#x20;   \[PIPELINE] Refining timestamp...

&#x20;   \[PIPELINE] Extracting frame...

&#x20;   \[PIPELINE] Search completed.



Do not remove useful existing debugging output unless it is

redundant.



============================================================

&#x20;                PERFORMANCE REQUIREMENT

============================================================



The entire purpose of the pipeline is to avoid unnecessary

expensive work.



Therefore:



&#x20;   subtitles → cheapest

&#x20;   Whisper   → more expensive

&#x20;   OCR       → fallback / expensive



Do not:



&#x20;   subtitle + full Whisper + full OCR



when subtitles already provide a reliable answer.



The pipeline should escalate only when necessary.



============================================================

&#x20;               CURRENT BEHAVIOR PRESERVATION

============================================================



This is extremely important.



Do NOT change:



&#x20;   - existing public function names

&#x20;   - existing service responsibilities

&#x20;   - existing successful behavior

&#x20;   - existing working Whisper logic

&#x20;   - existing subtitle logic

&#x20;   - existing frame extraction behavior

&#x20;   - yt-dlp's fundamental download behavior



unless a modification is strictly necessary to integrate the

new pipeline.



If a service needs a change, make the smallest compatible

change possible.



Do not perform unrelated refactoring.



Do not rename the entire project structure.



Do not introduce unnecessary frameworks.



Do not add PaddleOCR.



Do not replace Whisper.



Do not replace EasyOCR.



Do not replace yt-dlp.



============================================================

&#x20;                FASTAPI PREPARATION

============================================================



The project will later expose this pipeline through FastAPI.



Therefore design `pipeline.py` as framework-independent

application logic.



IMPORTANT:



Do NOT put FastAPI code inside the services.



Do NOT make the services depend on FastAPI.



The desired architecture is:



&#x20;   FastAPI route

&#x20;         ↓

&#x20;     pipeline.py

&#x20;         ↓

&#x20;      services



The pipeline should be callable from normal Python code

without starting a web server.



Do NOT implement the FastAPI server unless the existing

project already requires it.



Only make the pipeline cleanly usable by a future FastAPI

endpoint.



============================================================

&#x20;                FILE STRUCTURE

============================================================



Preserve the current structure as much as possible.



A reasonable final structure is:



&#x20;   Quest1/

&#x20;   │

&#x20;   ├── pipeline.py

&#x20;   ├── test\_visual.py

&#x20;   │

&#x20;   └── services/

&#x20;       ├── dialogue\_search.py

&#x20;       ├── whisper\_service.py

&#x20;       ├── frame\_extractor.py

&#x20;       ├── frame\_text\_search.py

&#x20;       ├── subtitle\_search.py

&#x20;       └── video\_downloader.py



Do not create unnecessary files.



============================================================

&#x20;                 CODE QUALITY

============================================================



The resulting code should be production-oriented.



Use:



&#x20;   - clear function names

&#x20;   - type hints where useful

&#x20;   - docstrings for important functions

&#x20;   - constants/configuration instead of magic numbers

&#x20;   - small helper functions

&#x20;   - consistent return structures

&#x20;   - proper exception handling

&#x20;   - no duplicated logic



Avoid:



&#x20;   - giant monolithic functions

&#x20;   - deeply nested conditionals

&#x20;   - duplicated OCR/Whisper code

&#x20;   - hardcoded thresholds throughout the project

&#x20;   - unnecessary dependencies



============================================================

&#x20;               PIPELINE API

============================================================



Create a clean main entry point such as:



&#x20;   search\_video(

&#x20;       source,

&#x20;       target,

&#x20;       ...

&#x20;   )



where:



&#x20;   source = URL or local video path

&#x20;   target = text/dialogue to find



It should be possible to call:



&#x20;   result = search\_video(

&#x20;       source="video.mp4",

&#x20;       target="In my younger age"

&#x20;   )



and also:



&#x20;   result = search\_video(

&#x20;       source="https://...",

&#x20;       target="In my younger age"

&#x20;   )



without changing the rest of the code.



============================================================

&#x20;                IMPORTANT TESTING

============================================================



After making the changes:



1\. Test with a local 720p video.



2\. Test with the same video at 144p.



3\. Test a target that exists in subtitles.



4\. Test a target that does not exist in subtitles but exists

&#x20;  in audio.



5\. Test a target that exists only visually in the video.



6\. Test a target that does not exist anywhere.



7\. Test a URL input.



8\. Test an invalid/unreadable input.



9\. Verify that OCR does NOT produce false positives from

&#x20;  tiny text such as "M".



10\. Verify that the final frame number corresponds to the

&#x20;   returned timestamp.



============================================================

&#x20;                 FINAL INSTRUCTION

============================================================



Before editing:



&#x20;   1. Inspect the existing project.

&#x20;   2. Understand all current service interfaces.

&#x20;   3. Do not assume function signatures.

&#x20;   4. Reuse existing implementations wherever possible.



Then:



&#x20;   1. Modify only services that require changes for the new

&#x20;      pipeline.

&#x20;   2. Implement the central pipeline.py.

&#x20;   3. Preserve existing behavior.

&#x20;   4. Make the pipeline modular and FastAPI-ready.

&#x20;   5. Run the existing tests/scripts.

&#x20;   6. Fix integration errors caused by the changes.

&#x20;   7. Do not make unrelated improvements.



At the end, provide a concise report containing:



&#x20;   - files modified

&#x20;   - what changed in each file

&#x20;   - final pipeline flow

&#x20;   - how URL input works

&#x20;   - how local file input works

&#x20;   - when Whisper is triggered

&#x20;   - when OCR is triggered

&#x20;   - how timestamp verification works

&#x20;   - how the final frame is selected

&#x20;   - any remaining limitations



Do not merely describe what should be done.

Actually implement the changes in the existing project.







\-----------------------------------------------------------------------------------------------------





**=============================**

**Step 8 - FastAPI Introduction**

**=============================**

You are working on my existing Python video-search project.



IMPORTANT:

I want to introduce FastAPI into the project WITHOUT changing the existing business/search logic.



CURRENT PROJECT BEHAVIOR MUST REMAIN EXACTLY THE SAME.



==================================================

CURRENT PIPELINE

==================================================



The existing pipeline is approximately:



Input:

&#x20;   URL OR LOCAL VIDEO FILE

&#x20;       |

&#x20;       v

Download video if URL

&#x20;       |

&#x20;       v

Subtitle search

&#x20;       |

&#x20;       |-- match found

&#x20;       |       |

&#x20;       |       v

&#x20;       |   verify with Whisper audio window

&#x20;       |       |

&#x20;       |       |-- verified --> extract best frame --> return

&#x20;       |       |

&#x20;       |       |-- not verified --> full Whisper search

&#x20;       |

&#x20;       |-- no subtitle match

&#x20;               |

&#x20;               v

&#x20;       Full Whisper audio search

&#x20;               |

&#x20;               |-- match --> extract frame --> return

&#x20;               |

&#x20;               |-- no match

&#x20;                       |

&#x20;                       v

&#x20;                   OCR search

&#x20;                       |

&#x20;                       |-- match --> return

&#x20;                       |

&#x20;                       |-- no match --> not found



The existing `pipeline.py` already implements this orchestration through:



&#x20;   search\_video(source, target, ...)



There is also:



&#x20;   process\_video(video\_path, target)



for backward compatibility.



==================================================

CURRENT SERVICES

==================================================



The project currently contains services similar to:



services/

&#x20;   video\_downloader.py

&#x20;   subtitle\_search.py

&#x20;   transcription.py

&#x20;   dialogue\_search.py

&#x20;   frame\_text\_search.py

&#x20;   frame\_extractor.py



And:



&#x20;   pipeline.py



The existing services contain working logic.



DO NOT rewrite their algorithms.



DO NOT optimize them.



DO NOT refactor them.



DO NOT change their thresholds.



DO NOT change their OCR behavior.



DO NOT change Whisper behavior.



DO NOT change subtitle behavior.



DO NOT change video downloading behavior.



DO NOT change the return structure of `search\_video()` unless absolutely required for API serialization. If serialization requires adaptation, create a separate API serialization layer rather than modifying the pipeline.



==================================================

CURRENT KNOWN LIMITATIONS

==================================================



There are two known problems, but THEY MUST NOT BE FIXED NOW:



1\. OCR is not sufficiently reliable for very bad-quality videos.



2\. Subtitle search currently does not robustly try all possible subtitle formats/languages. It may currently focus on English/en-US.



DO NOT TOUCH EITHER OF THESE.



We will solve them later.



The current task is ONLY to add FastAPI.



==================================================

GOAL

==================================================



Create a clean FastAPI application around the existing pipeline.



The API must accept:



A) A URL



OR



B) A local uploaded video file



along with:



&#x20;   target



The API should execute the EXISTING:



&#x20;   search\_video()



pipeline.



The FastAPI layer should NOT duplicate the search logic.



There should be exactly one source of truth for the search pipeline:



&#x20;   pipeline.search\_video()



==================================================

DESIRED ARCHITECTURE

==================================================



Create a structure similar to:



project\_root/

│

├── main.py

├── pipeline.py

├── requirements.txt

│

├── api/

│   ├── \_\_init\_\_.py

│   ├── routes.py

│   └── schemas.py

│

├── services/

│   ├── \_\_init\_\_.py

│   ├── video\_downloader.py

│   ├── subtitle\_search.py

│   ├── transcription.py

│   ├── dialogue\_search.py

│   ├── frame\_text\_search.py

│   └── frame\_extractor.py

│

├── downloads/

│

├── results/

│

└── uploads/



You may adjust the exact folder structure if the current project structure requires it, but keep the architecture clean and simple.



==================================================

FASTAPI ENTRY POINT

==================================================



Create a FastAPI application.



For example:



&#x20;   main.py



should create:



&#x20;   app = FastAPI(...)



and include the API router.



The server should be runnable with:



&#x20;   uvicorn main:app --reload



Do not execute the search pipeline merely by importing `main.py`.



==================================================

API DESIGN

==================================================



Create an endpoint such as:



&#x20;   POST /api/search



It should support two input modes.



MODE 1:

URL



Example request:



&#x20;   target = "In my younger age"

&#x20;   url = "https://..."



MODE 2:

FILE UPLOAD



Example multipart request:



&#x20;   video = <uploaded video>

&#x20;   target = "In my younger age"



The API must make sure exactly one video source is supplied.



If both URL and file are supplied:



&#x20;   return HTTP 400



If neither is supplied:



&#x20;   return HTTP 400



Do not modify `pipeline.search\_video()` to handle FastAPI-specific request objects.



Instead, the API layer should resolve the input into a normal filesystem path or URL string and then call:



&#x20;   search\_video(source, target)



==================================================

FILE UPLOAD HANDLING

==================================================



For uploaded videos:



1\. Create an `uploads/` directory if it doesn't exist.

2\. Generate a safe unique filename.

3\. Save the uploaded file there.

4\. Pass the saved file path to:



&#x20;      search\_video()



Do not pass the FastAPI UploadFile object into the pipeline.



The pipeline should continue receiving a normal string path.



Do not overwrite an existing uploaded file.



==================================================

URL HANDLING

==================================================



For URL requests:



Pass the URL directly to:



&#x20;   search\_video()



Do NOT duplicate `download\_video()` in the API layer.



The existing pipeline already knows how to handle URLs.



Therefore:



FastAPI

&#x20;   |

&#x20;   v

search\_video(URL, target)

&#x20;   |

&#x20;   v

existing pipeline

&#x20;   |

&#x20;   v

existing video\_downloader.py



==================================================

RESULT HANDLING

==================================================



The existing pipeline result contains fields such as:



&#x20;   found

&#x20;   source

&#x20;   target

&#x20;   matched\_text

&#x20;   score

&#x20;   timestamp

&#x20;   end\_timestamp

&#x20;   frame\_number

&#x20;   frame

&#x20;   video\_path



The `frame` field contains an OpenCV/Numpy image and cannot be returned directly as JSON.



DO NOT modify the pipeline result just for FastAPI.



Instead, create an API response/serialization layer.



The API response should contain JSON-safe fields such as:



&#x20;   {

&#x20;       "found": true,

&#x20;       "source": "whisper",

&#x20;       "target": "In my younger age",

&#x20;       "matched\_text": "...",

&#x20;       "score": 87.5,

&#x20;       "timestamp": 75.42,

&#x20;       "end\_timestamp": 79.22,

&#x20;       "frame\_number": 1808,

&#x20;       "video\_path": "...",

&#x20;       "frame\_url": "..."

&#x20;   }



If a frame exists:



1\. Save the returned frame into a `results/` directory.

2\. Generate a unique filename.

3\. Return a URL/path through which the frame can later be accessed.



For example:



&#x20;   /api/results/<filename>



Use FastAPI's static file serving or an appropriate response mechanism.



Do not return the raw numpy/OpenCV frame in JSON.



If no frame exists:



&#x20;   frame\_url = null



==================================================

RESULT IMAGE

==================================================



The current CLI code manually does:



&#x20;   cv2.imwrite("result\_frame.jpg", result\["frame"])



Move this responsibility into the API layer.



Do NOT add this behavior to:



&#x20;   pipeline.py



The pipeline should continue returning the frame as it currently does.



The API adapter should save it.



==================================================

ERROR HANDLING

==================================================



Implement clean API-level errors.



Examples:



Invalid input:



&#x20;   HTTP 400



No URL and no file:



&#x20;   HTTP 400



Both URL and file:



&#x20;   HTTP 400



Invalid/nonexistent local file:



&#x20;   HTTP 400 or 404



Pipeline failure:



&#x20;   HTTP 500



Do not hide the original exception during development.



Log useful information.



==================================================

ASYNC / BLOCKING WARNING

==================================================



`search\_video()` is currently synchronous and computationally expensive.



DO NOT rewrite the pipeline as async.



DO NOT convert Whisper/OCR/OpenCV functions into async.



For now, FastAPI may call the existing synchronous pipeline safely through an appropriate threadpool/background execution mechanism so that the API architecture is correct.



However, DO NOT introduce a complicated job queue, Celery, Redis, database, WebSocket system, or distributed processing system.



Keep this implementation simple.



We can introduce proper background jobs later if required.



==================================================

BACKWARD COMPATIBILITY

==================================================



The following must continue working exactly as before:



&#x20;   python main.py



if `main.py` currently contains a CLI test, preserve that behavior appropriately or move the CLI test into a separate file such as:



&#x20;   test\_pipeline.py



But do NOT break existing direct usage of:



&#x20;   search\_video()



and:



&#x20;   process\_video()



The existing services must remain usable independently.



==================================================

SCHEMAS

==================================================



Create Pydantic schemas where appropriate.



For example:



Search response:



&#x20;   SearchResponse



with fields:



&#x20;   found: bool

&#x20;   source: Optional\[str]

&#x20;   target: str

&#x20;   matched\_text: Optional\[str]

&#x20;   score: float

&#x20;   timestamp: Optional\[float]

&#x20;   end\_timestamp: Optional\[float]

&#x20;   frame\_number: Optional\[int]

&#x20;   video\_path: Optional\[str]

&#x20;   frame\_url: Optional\[str]



Do not expose raw internal objects such as:



&#x20;   numpy.ndarray



through Pydantic.



==================================================

ROUTES

==================================================



Keep routes separate from business logic.



For example:



&#x20;   api/routes.py



should contain the endpoint definitions.



It should roughly perform:



1\. Validate request.

2\. Save uploaded file if necessary.

3\. Determine source.

4\. Call `search\_video()`.

5\. Convert result to API-safe response.

6\. Save result frame if present.

7\. Return JSON.



It MUST NOT implement:



\- subtitle searching

\- Whisper searching

\- OCR searching

\- fuzzy matching

\- frame extraction

\- video downloading



Those already belong to the existing services/pipeline.



==================================================

SERIALIZATION

==================================================



Create a dedicated helper if useful:



&#x20;   serialize\_search\_result(...)



This function should convert:



&#x20;   pipeline result

&#x20;       ->

&#x20;   API-safe response



Do not alter the pipeline's internal return structure.



==================================================

STATIC RESULT FILES

==================================================



Configure FastAPI to expose saved result images.



For example:



&#x20;   /api/results/<filename>



The exact implementation is up to you.



Make sure paths are safe and files cannot be accessed through arbitrary path traversal.



==================================================

CLEANUP

==================================================



Do NOT automatically delete downloaded videos or uploaded files yet.



We may need them later for debugging.



Do not introduce aggressive cleanup logic.



==================================================

DEPENDENCIES

==================================================



Add only the FastAPI-related dependencies that are actually necessary.



For example:



&#x20;   fastapi

&#x20;   uvicorn

&#x20;   python-multipart



Do not change existing OCR/Whisper/Paddle dependencies.



Do not upgrade/downgrade existing ML libraries.



Do not modify the current Python environment unless absolutely necessary.



==================================================

IMPORTANT: DO NOT CHANGE EXISTING SERVICES

==================================================



This is the most important requirement.



DO NOT modify the implementation logic of:



&#x20;   services/video\_downloader.py

&#x20;   services/subtitle\_search.py

&#x20;   services/transcription.py

&#x20;   services/dialogue\_search.py

&#x20;   services/frame\_text\_search.py

&#x20;   services/frame\_extractor.py



Also do not modify the actual search algorithm in:



&#x20;   pipeline.py



The FastAPI implementation should wrap the current pipeline.



If an import must be adjusted because of the new project structure, make ONLY the minimum import/path change.



Do not change the behavior.



==================================================

CLI COMPATIBILITY

==================================================



The current CLI invocation effectively does:



&#x20;   result = search\_video(

&#x20;       VIDEO\_PATH\_OR\_URL,

&#x20;       TARGET

&#x20;   )



and then writes:



&#x20;   result\["frame"]



to an image.



That behavior must continue to work.



FastAPI is an additional interface, not a replacement for the existing pipeline.



==================================================

FUTURE EXTENSIBILITY

==================================================



Design the API layer so that later we can improve:



1\. OCR quality / preprocessing / upscaling

2\. Subtitle discovery across different subtitle formats/languages

3\. Whisper model selection

4\. Search thresholds

5\. Processing status/progress

6\. Background job execution



WITHOUT redesigning the FastAPI API completely.



But DO NOT implement those future improvements now.



==================================================

TESTING

==================================================



After implementing the FastAPI layer, verify:



TEST 1:

Start server:



&#x20;   uvicorn main:app --reload



TEST 2:

Open:



&#x20;   /docs



and verify Swagger UI works.



TEST 3:

Send a URL request.



The existing pipeline should execute:



&#x20;   URL

&#x20;   -> download

&#x20;   -> subtitle search

&#x20;   -> Whisper

&#x20;   -> OCR fallback

&#x20;   -> result



exactly as before.



TEST 4:

Send a local uploaded video.



The API should:



&#x20;   upload

&#x20;   -> save temporary/persistent file

&#x20;   -> search\_video(local\_path, target)

&#x20;   -> return result



TEST 5:

Verify the returned frame URL works.



TEST 6:

Verify a "not found" result is returned cleanly.



==================================================

DO NOT DO THESE THINGS

==================================================



DO NOT:



\- rewrite OCR

\- add upscaling

\- change EasyOCR

\- add PaddleOCR

\- modify Whisper

\- change Whisper model

\- change subtitle discovery

\- add new subtitle providers

\- change fuzzy matching

\- change thresholds

\- redesign pipeline logic

\- introduce Celery

\- introduce Redis

\- introduce a database

\- introduce authentication

\- introduce Docker

\- introduce Kubernetes

\- introduce WebSockets

\- introduce frontend UI

\- introduce job queues

\- modify ML dependencies unnecessarily



Those are separate future tasks.



==================================================

FINAL EXPECTATION

==================================================



At the end, I want a clean architecture like:



&#x20;                   ┌──────────────────┐

&#x20;                   │     FastAPI      │

&#x20;                   │   /api/search    │

&#x20;                   └────────┬─────────┘

&#x20;                            │

&#x20;                   URL or uploaded file

&#x20;                            │

&#x20;                            v

&#x20;                   ┌──────────────────┐

&#x20;                   │   API Adapter    │

&#x20;                   │ validation/file  │

&#x20;                   │ saving/response  │

&#x20;                   └────────┬─────────┘

&#x20;                            │

&#x20;                            v

&#x20;                   ┌──────────────────┐

&#x20;                   │    pipeline.py   │

&#x20;                   │  search\_video()  │

&#x20;                   └────────┬─────────┘

&#x20;                            │

&#x20;         ┌──────────────────┼──────────────────┐

&#x20;         │                  │                  │

&#x20;         v                  v                  v

&#x20;    Subtitles           Whisper              OCR

&#x20;         │                  │                  │

&#x20;         └──────────────────┼──────────────────┘

&#x20;                            │

&#x20;                            v

&#x20;                   Frame Extraction

&#x20;                            │

&#x20;                            v

&#x20;                   API-safe JSON result



The critical architectural principle is:



FASTAPI SHOULD WRAP THE EXISTING PIPELINE,

NOT REIMPLEMENT THE EXISTING PIPELINE.



Before making changes, inspect the current project files and understand their imports and existing entry points.



Make the smallest set of changes necessary to introduce FastAPI.



After changes, clearly report:



1\. Files created

2\. Files modified

3\. Files intentionally NOT modified

4\. How to start the FastAPI server

5\. Example URL request

6\. Example file-upload request

7\. Swagger URL

8\. Exact API response structure

9\. Confirmation that existing search behavior was preserved

10\. Any import/path changes that were necessary



Do not silently modify unrelated files.

\-----------------------------------------------------------------------------------------------------

**=========================================**

**Step 10 - Pipeline Change for optimization**

**=========================================**

Modify the existing Quest1 project to fix ONLY the way Whisper/audio search handles remote video URLs.



IMPORTANT: DO NOT redesign the pipeline. DO NOT change existing service logic. DO NOT change the API contract. DO NOT change OCR behavior. DO NOT change subtitle behavior. DO NOT change dialogue matching behavior. DO NOT change frame extraction behavior unless absolutely necessary to maintain compatibility with this change.



==================================================

CURRENT PROBLEM

==================================================



For a remote URL, the current pipeline does this conceptually:



URL

&#x20; -> subtitle search

&#x20; -> get direct "bestaudio/best" stream URL

&#x20; -> pass that remote stream URL directly into Whisper

&#x20; -> Whisper takes a very long time / behaves inefficiently



The current pipeline contains logic similar to:



&#x20;   media\_input = get\_media\_stream\_url(source, "bestaudio/best")



and later:



&#x20;   transcription\_result = transcribe\_video(media\_input)



This must be changed.



Whisper should NOT be given a remote YouTube/media stream URL.



==================================================

DESIRED BEHAVIOR

==================================================



For a URL input, the pipeline must work like this:



&#x20;                   URL

&#x20;                    |

&#x20;                    v

&#x20;            Subtitle search

&#x20;                    |

&#x20;            +-------+-------+

&#x20;            |               |

&#x20;         FOUND             NOT FOUND

&#x20;            |               |

&#x20;            v               v

&#x20;     Verify with audio   Download AUDIO ONLY

&#x20;            |               |

&#x20;      +-----+-----+         v

&#x20;      |           |       Whisper

&#x20;   verified     failed       |

&#x20;      |           |          v

&#x20;      |           +------> Dialogue search

&#x20;      |                      |

&#x20;      v                  +---+---+

&#x20;  Extract frame         |       |

&#x20;                        FOUND   NOT FOUND

&#x20;                          |       |

&#x20;                          v       v

&#x20;                   Extract frame  Download FULL VIDEO

&#x20;                                     |

&#x20;                                     v

&#x20;                                    OCR



The critical requirement is:



FOR URL INPUTS:

\- Subtitle search must NOT download the full video.

\- Whisper must download/process AUDIO ONLY.

\- Full video must NOT be downloaded before OCR is required.

\- Full video download should happen ONLY when OCR is reached.

\- If a Whisper match is found, do NOT download the full video merely because Whisper found it.

\- Frame extraction should continue using the existing direct-stream/fallback mechanism.

\- If direct frame extraction fails and the existing implementation requires a full-video fallback, that fallback may still occur because it is necessary to produce the requested result frame. Do not redesign frame extraction.



FOR LOCAL VIDEO FILE INPUTS:

\- Preserve the current behavior exactly.

\- Continue using the local video file directly.

\- Do not introduce unnecessary downloads.



==================================================

IMPLEMENTATION REQUIREMENT

==================================================



Create a separate AUDIO-ONLY download path for remote URLs.



Prefer adding a helper to:



&#x20;   services/video\_downloader.py



such as:



&#x20;   download\_audio(url, output\_dir="downloads")



The existing:



&#x20;   download\_video(...)



must remain responsible for FULL VIDEO downloads and must NOT be repurposed into an audio downloader.



The existing full-video downloader behavior must remain intact.



The audio downloader should use yt-dlp to retrieve an audio-only media stream/file suitable for Whisper.



Do NOT unnecessarily convert the audio using additional tools unless required by the existing environment.



The resulting audio path must be a normal local file path that can safely be passed to:



&#x20;   transcribe\_video(audio\_path)



==================================================

PIPELINE CHANGE

==================================================



Modify ONLY the relevant part of pipeline.py.



Current problematic behavior:



&#x20;   media\_input = get\_media\_stream\_url(source, "bestaudio/best")



&#x20;   ...



&#x20;   transcription\_result = transcribe\_video(media\_input)



Replace this architecture with:



For URL:

&#x20;   1. Resolve URL as currently required for subtitle processing.

&#x20;   2. Perform subtitle search exactly as before.

&#x20;   3. If subtitle verification requires Whisper/audio:

&#x20;          download AUDIO ONLY

&#x20;          pass the LOCAL AUDIO FILE to verify\_audio\_window()

&#x20;   4. If full Whisper search is required:

&#x20;          reuse the already downloaded local audio file if available

&#x20;          pass that LOCAL AUDIO FILE to transcribe\_video()

&#x20;   5. Do NOT download the full video for Whisper.

&#x20;   6. If Whisper fails:

&#x20;          only then download the FULL VIDEO

&#x20;          run existing OCR code exactly as before.



Avoid downloading the same audio more than once during a single pipeline execution.



For example, conceptually:



&#x20;   audio\_path = None



&#x20;   if URL and audio is required:

&#x20;       audio\_path = download\_audio(source)



&#x20;   if subtitle candidate exists:

&#x20;       verify\_audio\_window(

&#x20;           audio\_path,

&#x20;           ...

&#x20;       )



&#x20;   if full Whisper is required:

&#x20;       transcribe\_video(audio\_path)



&#x20;   if Whisper fails:

&#x20;       video\_path = download\_video(source)

&#x20;       search\_frames(video\_path, ...)



The exact implementation should fit the current project structure and existing function signatures.



==================================================

VERY IMPORTANT: PRESERVE EXISTING SERVICE LOGIC

==================================================



DO NOT modify the internal algorithms of:



&#x20;   services/subtitle\_search.py

&#x20;   services/transcription.py

&#x20;   services/dialogue\_search.py

&#x20;   services/frame\_text\_search.py

&#x20;   services/frame\_extractor.py



unless a tiny compatibility change is absolutely required because those functions currently assume a video path.



If verify\_audio\_window() or transcribe\_video() already accept a generic media path, simply pass the local audio path.



If they require a video container specifically, make the smallest possible compatibility change necessary to allow a local audio file.



DO NOT alter:

\- Whisper model

\- Whisper parameters

\- word timestamp logic

\- dialogue matching algorithm

\- RapidFuzz scoring

\- thresholds

\- OCR preprocessing

\- OCR sampling

\- OCR matching

\- subtitle matching

\- frame extraction algorithm

\- API response structure



==================================================

REUSE AUDIO

==================================================



An important optimization:



If a subtitle candidate is found and audio verification is required, download the audio once.



If subtitle verification fails and the pipeline proceeds to full Whisper search, reuse that same audio file.



DO NOT download the audio again.



Similarly, if no subtitles are found, download audio once for full Whisper.



==================================================

FULL VIDEO DOWNLOAD RULE

==================================================



This is the most important constraint.



For a URL:



DO NOT call:



&#x20;   download\_video(source)



during:

\- subtitle search

\- subtitle verification

\- full Whisper search



Only call full:



&#x20;   download\_video(source)



when:



&#x20;   subtitle search failed

&#x20;   AND

&#x20;   Whisper search failed

&#x20;   AND

&#x20;   OCR is actually required



Then:



&#x20;   downloaded\_video\_path = download\_video(source)



and continue with the EXISTING OCR implementation.



==================================================

FRAME RESULT

==================================================



Do not remove or break the existing final frame behavior.



When subtitle or Whisper finds a match:



&#x20;   extract\_frame(...)



must still produce:



\- frame

\- frame\_number

\- timestamp



using the existing mechanism.



Do not download the entire video simply to extract the frame if the current direct-stream extraction can handle it.



Keep the existing fallback behavior where necessary.



==================================================

OUTPUT/API CONTRACT

==================================================



DO NOT change the structure returned by search\_video().



It must continue returning:



&#x20;   {

&#x20;       "found": ...,

&#x20;       "source": ...,

&#x20;       "target": ...,

&#x20;       "matched\_text": ...,

&#x20;       "score": ...,

&#x20;       "timestamp": ...,

&#x20;       "end\_timestamp": ...,

&#x20;       "frame\_number": ...,

&#x20;       "frame": ...,

&#x20;       "video\_path": ...

&#x20;   }



Do not rename fields.



Do not remove fields.



Do not change the FastAPI request/response contract.



Do not modify main.py/API routes unless absolutely necessary for compatibility.



==================================================

LOCAL FILE BEHAVIOR

==================================================



For:



&#x20;   search\_video("video.mp4", target)



the behavior must remain equivalent to the current implementation.



No URL-specific downloading logic should affect local files.



==================================================

LOGGING

==================================================



Improve only the logging needed to make the new behavior obvious.



For example:



&#x20;   \[PIPELINE] Downloading audio only for Whisper...

&#x20;   \[PIPELINE] Audio download complete: ...

&#x20;   \[PIPELINE] Reusing downloaded audio for full Whisper search...

&#x20;   \[PIPELINE] Whisper search completed.

&#x20;   \[PIPELINE] No subtitle/audio match.

&#x20;   \[PIPELINE] Downloading full video for OCR...



This is useful because we must be able to verify that a full video download is NOT happening before OCR.



Do not add excessive unrelated logging.



==================================================

ERROR HANDLING

==================================================



If audio-only download fails:



\- Do not crash the entire API unnecessarily.

\- Continue according to the existing pipeline's fallback behavior.

\- If audio cannot be obtained, OCR may become the next available fallback.

\- Preserve the existing "not found" result behavior.



If full-video download fails when OCR is required:



\- return the existing empty/not-found result structure.



Do not introduce unrelated exception handling changes.



==================================================

CLEANUP

==================================================



Do not introduce a complicated storage system.



If temporary/local audio files are created, handle them sensibly.



Do not delete a file while it is still required by Whisper.



Do not break concurrent API requests by using one fixed shared audio filename.



Use a unique or URL/video-ID-based filename where appropriate.



Avoid changing existing download locations unless required.



==================================================

BACKWARD COMPATIBILITY

==================================================



The following must continue working:



1\. Local video:

&#x20;      search\_video("video5.mp4", "target")



2\. YouTube URL:

&#x20;      search\_video("https://youtu.be/...", "target")



3\. FastAPI endpoint using the same search\_video() pipeline.



4\. Existing process\_video() compatibility helper.



Do not change function names or public signatures unnecessarily.



==================================================

SCOPE RESTRICTION

==================================================



THIS TASK IS ONLY ABOUT:



&#x20;   REMOTE URL -> WHISPER SHOULD USE LOCAL AUDIO-ONLY DOWNLOAD



Do NOT use this task as an opportunity to fix or redesign:



\- OCR quality

\- OCR upscaling

\- PaddleOCR

\- EasyOCR

\- subtitle language handling

\- subtitle source discovery

\- subtitle fallback strategy

\- Whisper accuracy

\- Whisper model selection

\- dialogue matching algorithm

\- RapidFuzz thresholds

\- FastAPI architecture

\- authentication

\- database

\- caching system

\- frontend

\- background jobs

\- async redesign

\- API response redesign

\- frame extraction algorithm



Those are separate future tasks.



==================================================

VALIDATION

==================================================



After making the changes, inspect the project and verify:



CASE 1:

URL + subtitle match

&#x20;   -> subtitle search

&#x20;   -> audio-only download only if verification requires audio

&#x20;   -> Whisper verification

&#x20;   -> frame extraction

&#x20;   -> NO full video download unless frame extraction fallback specifically requires it



CASE 2:

URL + no subtitle + Whisper match

&#x20;   -> subtitle search

&#x20;   -> audio-only download

&#x20;   -> Whisper

&#x20;   -> frame extraction

&#x20;   -> NO full video download for OCR



CASE 3:

URL + no subtitle + Whisper no match

&#x20;   -> subtitle search

&#x20;   -> audio-only download

&#x20;   -> Whisper

&#x20;   -> full video download

&#x20;   -> OCR



CASE 4:

Local video

&#x20;   -> preserve existing behavior



Most importantly, confirm that this log sequence is possible:



&#x20;   \[PIPELINE] Searching subtitles without downloading full video...

&#x20;   \[PIPELINE] Downloading audio only for Whisper...

&#x20;   \[PIPELINE] Executing full Whisper audio search...

&#x20;   \[PIPELINE] Whisper match found...

&#x20;   \[PIPELINE] Full video download skipped.



And when Whisper fails:



&#x20;   \[PIPELINE] Executing full Whisper audio search...

&#x20;   \[PIPELINE] Whisper audio search yielded no match.

&#x20;   \[PIPELINE] Downloading full video for OCR...



==================================================

FINAL REQUIREMENT

==================================================



Before finishing:



1\. Review every changed file.

2\. Make sure no unrelated files were modified.

3\. Make sure existing service algorithms remain unchanged.

4\. Make sure the FastAPI API contract remains unchanged.

5\. Make sure full video download occurs only when OCR is required, except for an unavoidable existing frame-extraction fallback.

6\. Make sure audio is downloaded only once and reused for subtitle verification + full Whisper search.

7\. Do not rewrite the project unnecessarily.

8\. Keep the implementation clean, production-oriented, and compatible with the current Quest1 pipeline.



The goal is NOT to make the pipeline more complex.



The goal is specifically:



&#x20;   URL

&#x20;     -> subtitles without full video

&#x20;     -> LOCAL AUDIO ONLY for Whisper

&#x20;     -> if Whisper fails

&#x20;     -> FULL VIDEO ONLY FOR OCR



Everything else must remain as it currently works.



**=============================**

**Step 11 - Frontend Generation**

**=============================**

Build a SIMPLE React JS frontend for the existing Quest1 FastAPI video search application.



IMPORTANT:

Do not redesign or modify the existing search algorithms/services.

Do not change Whisper.

Do not change subtitle logic.

Do not change OCR.

Do not change dialogue matching.

Do not change frame extraction.

Do not change the existing pipeline behavior.



This task is ONLY for:

1\. React frontend

2\. Minimal FastAPI integration required for frontend communication

3\. Real-time pipeline status/log display

4\. Proper final result display

5\. Displaying the extracted JPG frame



Keep the implementation simple and clean. Do NOT over-engineer it.



==================================================

GOAL

==================================================



Create a small React UI where the user can enter:



\- Video URL OR

\- Local video file



and enter:



\- Target text/dialogue



Then click:



&#x20;   Search



The UI should clearly show the pipeline progressing.



Example:



&#x20;   Quest1

&#x20;   Video Text Search



&#x20;   ┌─────────────────────────────────────────────┐

&#x20;   │ Video URL / File                            │

&#x20;   │ \[ https://youtu.be/...                    ] │

&#x20;   │                                             │

&#x20;   │ Target text                                 │

&#x20;   │ \[ In my younger age                       ] │

&#x20;   │                                             │

&#x20;   │              \[ Search ]                     │

&#x20;   └─────────────────────────────────────────────┘





While processing:



&#x20;   Processing

&#x20;   ─────────────────────────────────────────────



&#x20;   ✓ Input source resolved

&#x20;   ✓ Searching subtitles

&#x20;   ✓ Subtitle candidate found at 78.95s

&#x20;   ✓ Verifying candidate with Whisper

&#x20;   ● Executing full Whisper search...

&#x20;   ○ OCR fallback



The UI should make the current step visually obvious.



==================================================

TECHNOLOGY

==================================================



Use:



\- React

\- Vite

\- Plain CSS

\- fetch()

\- No Redux

\- No unnecessary UI framework

\- No complicated component architecture



Keep the project easy to understand.



Suggested structure:



frontend/

&#x20;   src/

&#x20;       App.jsx

&#x20;       App.css

&#x20;       main.jsx



Do not create dozens of components.



==================================================

INPUT UI

==================================================



Provide:



1\. Source input



The user must be able to provide either:



\- URL

\- Local video file



Use a simple input area.



For example:



&#x20;   Source

&#x20;   \[ https://youtu.be/... ]



and a file selector:



&#x20;   \[ Choose video ]



The frontend should determine whether the user supplied a URL or file.



If the backend currently has separate handling for URL/file, preserve that behavior.



Do not change the backend pipeline semantics.



2\. Target text



&#x20;   Target text

&#x20;   \[ In my younger age ]



3\. Search button



&#x20;   \[ Search ]



Disable the Search button while processing.



==================================================

PROCESSING UI

==================================================



This is very important.



The frontend must NOT simply show:



&#x20;   Loading...



Instead, display meaningful pipeline progress.



The backend should expose pipeline events/logs through a simple streaming mechanism.



Prefer:



&#x20;   Server-Sent Events (SSE)



over WebSockets because this application primarily needs:



&#x20;   Backend -> Frontend



progress updates.



Do not rewrite the pipeline.



The existing pipeline can emit progress messages/events at the appropriate points.



Example events:



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Resolving input source..."

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Searching subtitles..."

&#x20;   }



&#x20;   {

&#x20;       "type": "subtitle\_candidate",

&#x20;       "message": "Subtitle candidate found at 78.95s",

&#x20;       "timestamp": 78.95,

&#x20;       "score": 88.5

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Verifying candidate with Whisper..."

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Executing full Whisper audio search..."

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Whisper match found at 75.42s"

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Downloading full video for OCR..."

&#x20;   }



&#x20;   {

&#x20;       "type": "status",

&#x20;       "message": "Starting OCR..."

&#x20;   }



&#x20;   {

&#x20;       "type": "complete",

&#x20;       "result": {...}

&#x20;   }



The exact event implementation can be adapted to the current FastAPI structure.



==================================================

LOG DISPLAY

==================================================



Create a clean terminal-like or timeline-like processing panel.



For example:



&#x20;   PIPELINE

&#x20;   ─────────────────────────────────────────



&#x20;   ✓ Resolving input source

&#x20;     URL detected



&#x20;   ✓ Searching subtitles

&#x20;     No matching subtitle found



&#x20;   ✓ Downloading audio

&#x20;     Audio-only download



&#x20;   ● Running Whisper

&#x20;     Searching dialogue...



&#x20;   ○ OCR

&#x20;     Waiting



Each log should have a status:



&#x20;   ✓ completed

&#x20;   ● running

&#x20;   ○ pending



Do not display raw Python stack traces or ugly backend logs to the user.



Convert backend progress events into clean user-facing messages.



The UI should automatically scroll to the latest log.



==================================================

PIPELINE-SPECIFIC MESSAGES

==================================================



Use meaningful messages corresponding to the existing pipeline.



Examples:



Input:



&#x20;   "Resolving input source..."



Subtitle:



&#x20;   "Searching subtitles..."



If found:



&#x20;   "Subtitle candidate found at 00:01:18.950"



Verification:



&#x20;   "Verifying subtitle candidate with Whisper..."



If verification succeeds:



&#x20;   "Audio verification successful"



If verification fails:



&#x20;   "Subtitle verification failed"



Whisper:



&#x20;   "Searching full audio with Whisper..."



If found:



&#x20;   "Whisper match found at 00:01:15.420"



OCR:



&#x20;   "Subtitle and audio search failed"



&#x20;   "Downloading full video for OCR..."



&#x20;   "Running visual OCR search..."



If OCR finds something:



&#x20;   "OCR match found at ..."



Completion:



&#x20;   "Search completed"



Do not expose unnecessary internal implementation details.



==================================================

RESULT UI

==================================================



When the search succeeds, display a proper result card.



Example:



&#x20;   Search Result

&#x20;   ─────────────────────────────────────



&#x20;   ✓ Match Found



&#x20;   Source

&#x20;   Whisper



&#x20;   Target

&#x20;   "And presume nothing except this"



&#x20;   Matched Text

&#x20;   "presume nothing except this. if"



&#x20;   Confidence

&#x20;   87.10%



&#x20;   Start

&#x20;   00:01:15.420



&#x20;   End

&#x20;   00:01:19.220



&#x20;   Frame

&#x20;   1808



Then display the extracted JPG frame prominently.



Example:



&#x20;   Extracted Frame



&#x20;   ┌──────────────────────────────────┐

&#x20;   │                                  │

&#x20;   │          result\_frame.jpg        │

&#x20;   │                                  │

&#x20;   └──────────────────────────────────┘



Use an <img> element.



Do NOT embed the image as base64 unless absolutely necessary.



The FastAPI backend should expose the generated frame/image through a static route.



For example:



&#x20;   /results/{filename}



or an equivalent simple route.



The frontend should use that URL.



==================================================

RESULT IMAGE

==================================================



The existing pipeline returns:



&#x20;   frame



which is an OpenCV image.



Do not try to directly JSON serialize the numpy/OpenCV frame.



Instead:



1\. Save the extracted frame as JPG on the backend.

2\. Return a URL/path to that JPG in the API result.



Example:



&#x20;   {

&#x20;       "found": true,

&#x20;       "source": "whisper",

&#x20;       "target": "...",

&#x20;       "matched\_text": "...",

&#x20;       "score": 87.1,

&#x20;       "timestamp": "00:01:15.420",

&#x20;       "end\_timestamp": "00:01:19.220",

&#x20;       "frame\_number": 1808,

&#x20;       "frame\_url": "/results/abc123.jpg"

&#x20;   }



IMPORTANT:



Do not change the existing pipeline result fields unnecessarily.



If the existing API already has a frame URL mechanism, reuse it.



If it currently returns the OpenCV frame internally, add only the minimal API-layer conversion required to expose the JPG.



==================================================

NOT FOUND UI

==================================================



If nothing is found, display a clean message:



&#x20;   No Match Found



&#x20;   The target text was not found in:

&#x20;   • subtitles

&#x20;   • audio

&#x20;   • visual OCR



Do not treat this as an error.



==================================================

ERROR UI

==================================================



For actual errors:



&#x20;   Something went wrong



&#x20;   \[error message]



Keep errors separate from "target not found".



==================================================

LOADING STATE

==================================================



While searching:



\- Disable Search button

\- Show processing panel

\- Show current active step

\- Prevent accidental duplicate searches



After completion:



\- Re-enable Search

\- Keep logs visible

\- Show result



==================================================

FASTAPI CHANGES

==================================================



Make only the minimum FastAPI changes required.



Potential endpoints:



&#x20;   POST /search



or, if SSE is implemented:



&#x20;   POST /search

&#x20;   GET /search/{job\_id}/events



The exact structure should be chosen based on the existing FastAPI project.



Do NOT replace the existing pipeline.



The pipeline remains the source of truth.



The FastAPI layer should simply:



&#x20;   receive request

&#x20;       ↓

&#x20;   call search\_video()

&#x20;       ↓

&#x20;   forward progress events

&#x20;       ↓

&#x20;   return final result



==================================================

IMPORTANT: REAL-TIME LOGGING

==================================================



Do NOT fake the progress by showing predefined frontend messages with setTimeout().



The displayed progress should correspond to actual backend pipeline execution.



For example, if the backend is actually doing:



&#x20;   search\_video()

&#x20;       -> subtitle search

&#x20;       -> Whisper

&#x20;       -> OCR



the frontend should receive events from those actual stages.



Do not create fake progress such as:



&#x20;   wait 2 seconds

&#x20;   show subtitle

&#x20;   wait 3 seconds

&#x20;   show Whisper



That is NOT acceptable.



==================================================

BACKEND LOGGING DESIGN

==================================================



If the existing pipeline currently uses print():



&#x20;   print("\[PIPELINE] Searching subtitles...")



do not rewrite the pipeline's logic.



Add a minimal progress callback/event mechanism if necessary.



For example:



&#x20;   progress\_callback("Searching subtitles...")



or an equivalent lightweight mechanism.



The pipeline should continue functioning if no callback is provided.



This is important for backward compatibility.



Conceptually:



&#x20;   def search\_video(..., progress\_callback=None):



&#x20;       ...



&#x20;       print("\[PIPELINE] Searching subtitles...")



&#x20;       if progress\_callback:

&#x20;           progress\_callback(

&#x20;               "Searching subtitles..."

&#x20;           )



Do not alter the actual search algorithm.



The existing CLI behavior must continue working.



==================================================

API RESPONSE

==================================================



The frontend should receive structured final data.



Example:



&#x20;   {

&#x20;       "found": true,

&#x20;       "source": "whisper",

&#x20;       "target": "In my younger age",

&#x20;       "matched\_text": "...",

&#x20;       "score": 87.1,

&#x20;       "timestamp": "00:01:15.420",

&#x20;       "end\_timestamp": "00:01:19.220",

&#x20;       "frame\_number": 1808,

&#x20;       "frame\_url": "/results/result\_abc123.jpg"

&#x20;   }



If the existing API uses slightly different fields, preserve the existing fields.



Do NOT break current API clients.



==================================================

UI DESIGN

==================================================



Keep it clean and modern but simple.



Use:



\- white/light background

\- centered content

\- subtle borders

\- rounded cards

\- readable typography

\- one primary button

\- clear status indicators

\- responsive layout



Avoid:



\- gradients everywhere

\- excessive animations

\- huge dashboards

\- unnecessary navigation

\- sidebar

\- authentication UI

\- complicated charts

\- excessive icons



The application should feel like a clean developer tool.



Suggested layout:



\------------------------------------------------



&#x20;                   Quest1



&#x20;           Video Text Search



&#x20;   Search a dialogue or text inside

&#x20;   subtitles, audio, and video frames.



&#x20;   ┌─────────────────────────────────────────┐

&#x20;   │ Source                                  │

&#x20;   │ \[ URL or video path                  ]  │

&#x20;   │                                         │

&#x20;   │ Target text                             │

&#x20;   │ \[                                     ] │

&#x20;   │                                         │

&#x20;   │                 \[ Search ]               │

&#x20;   └─────────────────────────────────────────┘





&#x20;   Processing

&#x20;   ─────────────────────────────────────────



&#x20;   ✓ Resolving input

&#x20;   ✓ Searching subtitles

&#x20;   ● Searching audio with Whisper

&#x20;   ○ OCR





&#x20;   Search Result

&#x20;   ─────────────────────────────────────────



&#x20;   Match Found



&#x20;   Source       Whisper

&#x20;   Score        87.10%

&#x20;   Start        00:01:15.420

&#x20;   End          00:01:19.220



&#x20;   Target

&#x20;   "..."



&#x20;   Matched text

&#x20;   "..."



&#x20;   Extracted Frame



&#x20;   ┌─────────────────────────────────────────┐

&#x20;   │                                         │

&#x20;   │              IMAGE                      │

&#x20;   │                                         │

&#x20;   └─────────────────────────────────────────┘



\------------------------------------------------



==================================================

FILES

==================================================



Create a clean frontend structure.



Prefer:



&#x20;   frontend/

&#x20;       package.json

&#x20;       index.html

&#x20;       src/

&#x20;           main.jsx

&#x20;           App.jsx

&#x20;           App.css



Do not create unnecessary abstractions.



If the FastAPI project is currently structured differently, adapt to it rather than moving the backend around.



==================================================

CORS

==================================================



If React runs on:



&#x20;   http://localhost:5173



and FastAPI runs on:



&#x20;   http://127.0.0.1:8000



configure minimal FastAPI CORS support so the frontend can communicate with the backend.



Do not add authentication or other middleware.



==================================================

RUNNING

==================================================



The final project should be easy to run:



Backend:



&#x20;   uvicorn main:app --reload



Frontend:



&#x20;   cd frontend

&#x20;   npm install

&#x20;   npm run dev



Make sure the frontend points to the correct FastAPI base URL.



==================================================

STRICT SCOPE

==================================================



DO NOT change:



\- Whisper logic

\- Subtitle logic

\- OCR logic

\- Dialogue search logic

\- Frame extraction logic

\- Video downloader logic

\- Audio downloader logic

\- Search thresholds

\- Search ordering

\- Existing pipeline behavior

\- Existing FastAPI endpoint behavior unless required for frontend integration



Only add the minimum backend plumbing needed for:



1\. progress events

2\. result frame serving

3\. React communication

4\. CORS



==================================================

FINAL REQUIREMENT

==================================================



Before finishing:



1\. Start the FastAPI backend.

2\. Start the React frontend.

3\. Verify URL search works.

4\. Verify local file input works if the current API supports it.

5\. Verify pipeline progress is displayed.

6\. Verify real backend events are shown rather than fake timers.

7\. Verify final result is displayed cleanly.

8\. Verify timestamp formatting.

9\. Verify score display.

10\. Verify extracted JPG frame is visible.

11\. Verify "not found" is displayed correctly.

12\. Verify errors are displayed separately.

13\. Verify existing CLI/API behavior is not broken.



Keep everything SIMPLE.



The goal is a clean, functional React frontend for the existing Quest1 FastAPI pipeline — not a redesign of the backend.



