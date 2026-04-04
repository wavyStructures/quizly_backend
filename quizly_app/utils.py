import json
import os
import re
from django.conf import settings


VALID_ANSWERS = {"A", "B", "C", "D"}
INLINE_UPLOAD_LIMIT = 20 * 1024 * 1024  # 20 MB

def download_audio_from_youtube(url: str):
    """
    Lazily import downloader service only when needed.
    """
    try:
        from downloader.services import download_youtube_audio
    except ImportError as exc:
        raise ImportError(
            "yt-dlp is not installed. Install it to use YouTube download features."
        ) from exc

    return download_youtube_audio(url)


def get_gemini_client():
    """
    Lazily import and return a Gemini client.
    This prevents unrelated tests from failing if google-genai is not installed.
    """
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Install it to use Gemini features."
        ) from exc

    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in Django settings.")

    return genai.Client(api_key=api_key)


def get_genai_types():
    """
    Lazily import Gemini types only where needed.
    """
    try:
        from google.genai import types
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Install it to use Gemini features."
        ) from exc

    return types


def clean_gemini_json(text: str) -> str:
    """
    Remove optional markdown code fences around Gemini JSON output.
    """
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalize_answer(answer: str) -> str:
    """
    Normalize answers like 'a', 'A)', 'A - ...' to 'A'.
    """
    if not answer:
        return ""

    answer = answer.strip().upper()
    return answer[0] if answer and answer[0] in VALID_ANSWERS else answer


def validate_question_item(item: dict) -> dict:
    """
    Validate and normalize a single Gemini-generated question item.
    Returns the question in the structure expected by your Question model.
    """
    question = item.get("question")
    options = item.get("options", [])
    answer = normalize_answer(item.get("answer", ""))

    if not question:
        raise ValueError("A generated question is missing 'question'.")
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Each generated question must have exactly 4 options.")
    if answer not in VALID_ANSWERS:
        raise ValueError("Each generated question must have answer A, B, C, or D.")

    return {
        "question_title": question,
        "question_options": options,
        "answer": answer,
    }


def build_transcription_prompt() -> str:
    return (
        "Transcribe this audio accurately. "
        "Return only the transcript text. "
        "Do not summarize. Do not add commentary."
    )


def build_question_prompt(transcript: str, video_title: str) -> str:
    return f"""
Create exactly 10 multiple-choice questions in English about the following video.

Title:
{video_title}

Transcript:
---
{transcript}
---

IMPORTANT:
- Return only valid JSON.
- No Markdown.
- No explanation.
- Exactly 10 questions.
- Each question must have exactly 4 answer options.
- "answer" must only be "A", "B", "C", or "D".

Format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "A"
  }}
]
""".strip()


def transcribe_audio_with_gemini(audio_path: str) -> str:
    """
    Transcribe audio using Gemini.
    Uses inline bytes for smaller files and Files API for larger ones.
    """
    client = get_gemini_client()
    types = get_genai_types()
    prompt = build_transcription_prompt()

    file_size = os.path.getsize(audio_path)

    if file_size > INLINE_UPLOAD_LIMIT:
        uploaded_file = client.files.upload(file=audio_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, uploaded_file],
        )
    else:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type="audio/mpeg",
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, audio_part],
        )

    transcript = getattr(response, "text", None)
    if not transcript:
        raise ValueError("Gemini produced no transcript.")

    return transcript.strip()


def generate_questions_with_gemini(transcript: str, video_title: str) -> dict:
    """
    Generate quiz questions from a transcript using Gemini.
    """
    client = get_gemini_client()
    types = get_genai_types()
    prompt = build_question_prompt(transcript, video_title)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    response_text = getattr(response, "text", None)
    if not response_text:
        raise ValueError("Gemini returned no usable text.")

    cleaned = clean_gemini_json(response_text)

    try:
        questions_raw = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini returned invalid JSON.") from exc

    if not isinstance(questions_raw, list):
        raise ValueError("Gemini did not return a list of questions.")

    formatted_questions = [validate_question_item(item) for item in questions_raw]

    if len(formatted_questions) != 10:
        raise ValueError("Gemini must return exactly 10 questions.")

    return {
        "title": video_title,
        "description": f"Quiz generated from: {video_title}",
        "questions": formatted_questions,
    }


def generate_quiz_from_youtube(url: str) -> dict:
    """
    Full quiz generation workflow:
    1. Download audio from YouTube
    2. Transcribe audio with Gemini
    3. Generate quiz questions from transcript
    """
    try:
        # audio_path, video_title = download_youtube_audio(url)
        audio_path, video_title = download_audio_from_youtube(url)
    except Exception as exc:
        raise ValueError(f"Could not download audio: {exc}") from exc

    try:
        transcript = transcribe_audio_with_gemini(audio_path)
    except Exception as exc:
        raise ValueError(f"Could not transcribe audio: {exc}") from exc

    try:
        return generate_questions_with_gemini(transcript, video_title)
    except Exception as exc:
        raise ValueError(f"Could not generate quiz questions: {exc}") from exc





# import json
# import os
# import re

# from google import genai
# from google.genai import types
# from django.conf import settings

# from downloader.services import download_youtube_audio


# def clean_gemini_json(text: str) -> str:
#     text = text.strip()
#     text = re.sub(r"^```(?:json)?\s*", "", text)
#     text = re.sub(r"\s*```$", "", text)
#     return text.strip()


# def normalize_answer(ans: str) -> str:
#     ans = ans.strip().upper()
#     return ans[0] if ans and ans[0] in ["A", "B", "C", "D"] else ans


# def transcribe_audio_with_gemini(audio_path: str) -> str:
#     """
#     Transcribe audio using Gemini.
#     Uses inline bytes for smaller files and Files API for larger ones.
#     """
#     client = genai.Client(api_key=settings.GEMINI_API_KEY)

#     prompt = (
#         "Transcribe this audio accurately. "
#         "Return only the transcript text. "
#         "Do not summarize. Do not add commentary."
#     )

#     file_size = os.path.getsize(audio_path)

#     if file_size > 20 * 1024 * 1024:
#         uploaded_file = client.files.upload(file=audio_path)
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=[prompt, uploaded_file],
#         )
#     else:
#         with open(audio_path, "rb") as f:
#             audio_bytes = f.read()

#         audio_part = types.Part.from_bytes(
#             data=audio_bytes,
#             mime_type="audio/mpeg",
#         )

#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=[prompt, audio_part],
#         )

#     if not getattr(response, "text", None):
#         raise ValueError("Gemini produced no transcript")

#     return response.text.strip()


# def generate_questions_with_gemini(transcript: str, video_title: str) -> dict:
#     client = genai.Client(api_key=settings.GEMINI_API_KEY)

#     prompt = f"""
# Erstelle 5 Multiple-Choice-Fragen zu folgendem Video.

# Titel:
# {video_title}

# Transkript:
# ---
# {transcript}
# ---

# WICHTIG:
# - Antworte nur mit gültigem JSON.
# - Kein Markdown.
# - Keine Erklärung.
# - Genau 5 Fragen.
# - Jede Frage muss genau 4 Antwortoptionen haben.
# - "answer" muss nur "A", "B", "C" oder "D" sein.

# Format:
# [
#   {{
#     "question": "Fragetext",
#     "options": ["Option A", "Option B", "Option C", "Option D"],
#     "answer": "A"
#   }}
# ]
# """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             temperature=0.2,
#             response_mime_type="application/json",
#         ),
#     )

#     if not getattr(response, "text", None):
#         raise ValueError("Gemini returned no usable text")

#     cleaned = clean_gemini_json(response.text)
#     questions_raw = json.loads(cleaned)

#     if not isinstance(questions_raw, list):
#         raise ValueError("Gemini did not return a list of questions")

#     formatted = []

#     for q in questions_raw:
#         options = q.get("options", [])
#         answer = normalize_answer(q.get("answer", ""))

#         if not q.get("question"):
#             raise ValueError("A generated question is missing 'question'")
#         if not isinstance(options, list) or len(options) != 4:
#             raise ValueError("Each generated question must have exactly 4 options")
#         if answer not in ["A", "B", "C", "D"]:
#             raise ValueError("Each generated question must have answer A, B, C, or D")

#         formatted.append({
#             "question_title": q["question"],
#             "question_options": options,
#             "answer": answer,
#         })

#     return {
#         "title": video_title,
#         "description": f"Quiz generated from: {video_title}",
#         "questions": formatted,
#     }


# def generate_quiz_from_youtube(url: str) -> dict:
#     print("STEP 1: Downloading audio…")
#     try:
#         audio_path, video_title = download_youtube_audio(url)
#         print("Downloaded file:", audio_path)
#     except Exception as e:
#         print("DOWNLOAD ERROR:", repr(e))
#         raise ValueError(f"Could not download audio: {str(e)}")

#     print("STEP 2: Transcribing via Gemini…")
#     try:
#         transcript = transcribe_audio_with_gemini(audio_path)
#         print("Transcript length:", len(transcript))
#     except Exception as e:
#         print("TRANSCRIBE ERROR:", repr(e))
#         raise ValueError(f"Could not transcribe audio: {str(e)}")

#     print("STEP 3: Generating quiz…")
#     try:
#         quiz_data = generate_questions_with_gemini(transcript, video_title)
#         print("Quiz data keys:", quiz_data.keys())
#     except Exception as e:
#         print("QUIZ GENERATION ERROR:", repr(e))
#         raise ValueError(f"Could not generate quiz questions: {str(e)}")

#     print("STEP 4: DONE!")
#     return quiz_data