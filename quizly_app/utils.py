import os
import tempfile
import yt_dlp
import whisper
import json
import re
from google import generativeai as genai
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
        ydl.download([url])   

    for file in os.listdir(temp_dir):
        if file.startswith("audio"):
            return os.path.join(temp_dir, file)
    
    raise RuntimeError("Audio download failed.")


def transcribe_audio(audio_path: str) -> str:
    print("Whisper: loading model...")
    model = whisper.load_model("tiny")      

    print("Whisper: starting transcription...")
    result = model.transcribe(audio_path, fp16=False)

    print("Whisper: finished!")
    return result["text"]

def clean_gemini_json(raw_text: str) -> str:
    """
    Cleans Gemini output to extract valid JSON.
    """
    text = raw_text.strip()

    # Remove triple backticks
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
        # Remove optional "json" after opening ```
        if text.lower().startswith("json"):
            text = text[4:].strip()
    
    return text


def generate_questions_with_gemini(transcript: str) -> dict:

    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
Erstelle 5 Quizfragen basierend auf folgendem Video-Transkript:

---
{transcript}
---

Gib NUR gültiges JSON zurück.
"""
    response = model.generate_content(prompt)

    try:
        text = response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        raise ValueError("Gemini returned no usable text")

    print("RAW GEMINI TEXT:\n", text)  # Debug

    text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print("CLEANED TEXT:\n", text)
        raise ValueError("Invalid JSON from Gemini") from e


def generate_quiz_from_youtube(url: str) -> dict:
    print("STEP 1")
    audio_path = download_youtube_audio(url)

    print("STEP 2")
    transcript = transcribe_audio(audio_path)

    print("STEP 3")
    quiz_json = generate_questions_with_gemini(transcript)

    print("STEP 4", quiz_json)

    import json

    print("RAW LLM OUTPUT:", repr(quiz_json))

    if not quiz_json or not quiz_json.strip():
        raise ValueError("LLM returned empty output – cannot parse.")

    quiz_json_clean = quiz_json.strip()
    if quiz_json_clean.startswith("```"):
        quiz_json_clean = quiz_json_clean.strip("`")
        quiz_json_clean = quiz_json_clean.replace("json", "", 1).strip()

    try:
        return json.loads(quiz_json_clean)
    except json.JSONDecodeError as e:
        print("JSON parsing failed:", e)
        raise ValueError("LLM did not return valid JSON.") from e


