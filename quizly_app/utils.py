import os
import tempfile
import yt_dlp
import whisper
import json
import re
from google import genai
from django.conf import settings
import pprint


def download_youtube_audio(url: str) -> str:
    """
    Downloads YouTube audio using yt_dlp and returns the path to the audio file.
    """
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get("title", "YouTube Quiz")
        # ydl.download([url])   

    for file in os.listdir(temp_dir):
        if file.startswith("audio"):
            return os.path.join(temp_dir, file), video_title
    
    raise RuntimeError("Audio download failed.")


def transcribe_audio(audio_path: str) -> str:
    print("Whisper: loading model...")
    model = whisper.load_model("tiny")      

    print("Whisper: starting transcription...")
    result = model.transcribe(audio_path, fp16=False)

    print("Whisper: finished!")
    return result["text"]

def clean_gemini_json(text):
    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()

def generate_questions_with_gemini(transcript: str, video_title: str) -> dict:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
Erstelle 5 Quizfragen basierend auf folgendem Video-Transkript:

---
{transcript}
---

Antworte ausschließlich mit gültigem JSON.
Format:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",    
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned no usable text")

    print("RAW GEMINI TEXT:\n", response.text)

    cleaned = clean_gemini_json(response.text)

    try:
        questions_raw = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("CLEANED TEXT:\n", cleaned)
        raise ValueError("Invalid JSON from Gemini") from e


    # Transform Gemini format → your DB format
    formatted_questions = []

    for q in questions_raw:
        formatted_questions.append({
            "question_title": q["question"],
            "question_options": q["options"],
            "answer": q["answer"]
        })


    return {
        "title": video_title,
        "description": f"Quiz generated from: {video_title}",
        "questions": formatted_questions
    }


def generate_quiz_from_youtube(url: str) -> dict:
    print("STEP 1")
    audio_path, video_title = download_youtube_audio(url)

    print("STEP 2")
    transcript = transcribe_audio(audio_path)

    print("STEP 3")
    quiz_data = generate_questions_with_gemini(transcript, video_title)

    print("STEP 4", quiz_data)

    import json

    print("FINAL QUIZ DATA:", quiz_data)

    return quiz_data


