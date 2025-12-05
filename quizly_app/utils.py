import os
import tempfile
import yt_dlp
import whisper
from google import generativeai as genai
from django.conf import settings


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


# def generate_questions_with_gemini(transcript: str) -> dict:
#     """
#     Sends the transcript to Google Gemini API to generate quiz questions.
#     """

#     genai.configure(api_key=settings.GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.0-flash")

#     prompt = f"""
#     Du bist ein Quizgenerator.

#     Erstelle 5 Quizfragen basierend auf folgendem Video-Transkript:

#     ---
#     {transcript}
#     ---
    
#     Format als JSON:

#     {{
#       "title": "string",
#       "description": "string",
#       "questions": [
#         {{
#           "question_title": "string",
#           "question_options": ["A","B","C","D"],
#           "answer": "string"
#         }}
#       ]
#     }}
#     """

#     response = model.generate_content(prompt)
#     return response.text


def generate_questions_with_gemini(transcript: str) -> dict:
    """
    Sends the transcript to Google Gemini API to generate quiz questions.
    """

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Du bist ein Quizgenerator.

    Erstelle genau 5 Quizfragen basierend auf folgendem Video-Transkript:

    ---
    {transcript}
    ---

    Gib die Ausgabe AUSSCHLIESSLICH als gültiges JSON zurück:
    {{
      "title": "string",
      "description": "string",
      "questions": [
        {{
          "question_title": "string",
          "question_options": ["A","B","C","D"],
          "answer": "string"
        }}
      ]
    }}

    WICHTIG:
    - Keine Erklärungen.
    - Kein Markdown.
    - Keine ```json Code-Blöcke.
    - Keine Kommentare.
    - KEIN Text vor oder nach dem JSON.
    - Gib NUR das reine JSON zurück.
    """

    response = model.generate_content(prompt)
    return response.text

def generate_quiz_from_youtube(url: str) -> dict:
    print("STEP 1")
    audio_path = download_youtube_audio(url)

    print("STEP 2")
    transcript = transcribe_audio(audio_path)

    print("STEP 3")
    quiz_json = generate_questions_with_gemini(transcript)

    print("STEP 4", quiz_json)

    import json
    # return json.loads(quiz_json)

    # Debug: print the raw result
    print("RAW LLM OUTPUT:", repr(quiz_json))

    if not quiz_json or not quiz_json.strip():
        raise ValueError("LLM returned empty output – cannot parse.")

    # Sometimes models wrap JSON inside ```json ... ```
    quiz_json_clean = quiz_json.strip()
    if quiz_json_clean.startswith("```"):
        quiz_json_clean = quiz_json_clean.strip("`")
        quiz_json_clean = quiz_json_clean.replace("json", "", 1).strip()

    try:
        return json.loads(quiz_json_clean)
    except json.JSONDecodeError as e:
        print("JSON parsing failed:", e)
        raise ValueError("LLM did not return valid JSON.") from e



# def generate_quiz_from_youtube(url: str) -> dict:
#     """
#     Full pipeline:
#     1) download audio
#     2) transcribe
#     3) ask Gemini to create quiz
#     """

#     audio_path = download_youtube_audio(url)
#     transcript = transcribe_audio(audio_path)
#     quiz_json = generate_questions_with_gemini(transcript)

#     import json
#     try:
#         return json.loads(raw)
#     except Exception as e:
#         print("GEMINI RAW OUTPUT:", raw)
#         raise e

