import json
import os
import re

from google import genai
from google.genai import types
from django.conf import settings

from downloader.services import download_youtube_audio


def clean_gemini_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalize_answer(ans: str) -> str:
    ans = ans.strip().upper()
    return ans[0] if ans and ans[0] in ["A", "B", "C", "D"] else ans


def transcribe_audio_with_gemini(audio_path: str) -> str:
    """
    Transcribe audio using Gemini.
    Uses inline bytes for smaller files and Files API for larger ones.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        "Transcribe this audio accurately. "
        "Return only the transcript text. "
        "Do not summarize. Do not add commentary."
    )

    file_size = os.path.getsize(audio_path)

    if file_size > 20 * 1024 * 1024:
        uploaded_file = client.files.upload(file=audio_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, uploaded_file],
        )
    else:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type="audio/mpeg",
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, audio_part],
        )

    if not getattr(response, "text", None):
        raise ValueError("Gemini produced no transcript")

    return response.text.strip()


def generate_questions_with_gemini(transcript: str, video_title: str) -> dict:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
Erstelle 5 Multiple-Choice-Fragen zu folgendem Video.

Titel:
{video_title}

Transkript:
---
{transcript}
---

WICHTIG:
- Antworte nur mit gültigem JSON.
- Kein Markdown.
- Keine Erklärung.
- Genau 5 Fragen.
- Jede Frage muss genau 4 Antwortoptionen haben.
- "answer" muss nur "A", "B", "C" oder "D" sein.

Format:
[
  {{
    "question": "Fragetext",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "A"
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    if not getattr(response, "text", None):
        raise ValueError("Gemini returned no usable text")

    cleaned = clean_gemini_json(response.text)
    questions_raw = json.loads(cleaned)

    if not isinstance(questions_raw, list):
        raise ValueError("Gemini did not return a list of questions")

    formatted = []

    for q in questions_raw:
        options = q.get("options", [])
        answer = normalize_answer(q.get("answer", ""))

        if not q.get("question"):
            raise ValueError("A generated question is missing 'question'")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError("Each generated question must have exactly 4 options")
        if answer not in ["A", "B", "C", "D"]:
            raise ValueError("Each generated question must have answer A, B, C, or D")

        formatted.append({
            "question_title": q["question"],
            "question_options": options,
            "answer": answer,
        })

    return {
        "title": video_title,
        "description": f"Quiz generated from: {video_title}",
        "questions": formatted,
    }


def generate_quiz_from_youtube(url: str) -> dict:
    print("STEP 1: Downloading audio…")
    try:
        audio_path, video_title = download_youtube_audio(url)
        print("Downloaded file:", audio_path)
    except Exception as e:
        print("DOWNLOAD ERROR:", repr(e))
        raise ValueError(f"Could not download audio: {str(e)}")

    print("STEP 2: Transcribing via Gemini…")
    try:
        transcript = transcribe_audio_with_gemini(audio_path)
        print("Transcript length:", len(transcript))
    except Exception as e:
        print("TRANSCRIBE ERROR:", repr(e))
        raise ValueError(f"Could not transcribe audio: {str(e)}")

    print("STEP 3: Generating quiz…")
    try:
        quiz_data = generate_questions_with_gemini(transcript, video_title)
        print("Quiz data keys:", quiz_data.keys())
    except Exception as e:
        print("QUIZ GENERATION ERROR:", repr(e))
        raise ValueError(f"Could not generate quiz questions: {str(e)}")

    print("STEP 4: DONE!")
    return quiz_data