from django.conf import settings

import os
import re
import json
import logging
import yt_dlp
import whisper

from google import genai


logger = logging.getLogger(__name__)

if hasattr(settings, 'FFMPEG_PATH') and settings.FFMPEG_PATH:
    if os.path.exists(settings.FFMPEG_PATH):
        os.environ['PATH'] = settings.FFMPEG_PATH + os.pathsep + os.environ.get('PATH', '')
        logger.info(f"FFmpeg path configured: {settings.FFMPEG_PATH}")
    else:
        logger.warning(f"FFmpeg path specified but not found: {settings.FFMPEG_PATH}")
else:
    logger.info("No custom FFmpeg path specified, using system PATH")


class YouTubeDownloadError(Exception):
    """Raised when YouTube audio download fails"""
    pass


class TranscriptionError(Exception):
    """Raised when audio transcription fails"""
    pass


class QuizGenerationError(Exception):
    """Raised when quiz generation from transcript fails"""
    pass


def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL."""
    
    youtube_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/embed/[\w-]+',
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False


def download_youtube_audio(video_url: str) -> str:
    """Download audio from YouTube video."""
    
    try:
        import uuid
        temp_filename = os.path.join(settings.MEDIA_ROOT, f'temp_audio_{uuid.uuid4().hex}')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_filename + '.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

            filename = ydl.prepare_filename(info)
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Downloaded file not found at {filename}")
        
        return filename
        
    except Exception as e:
        raise YouTubeDownloadError(f"Failed to download YouTube audio: {str(e)}")


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using Whisper."""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
        
    except Exception as e:
        raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")


def generate_quiz_from_transcript(transcript: str, api_key: str) -> dict:
    """Generate a quiz from transcript using Google Gemini API."""
    
    try:
        prompt = f"""
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }},
    ...
    (exactly 10 questions)
  ]
}}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
{transcript}
"""
        
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        
        response_text = response.text.strip()
        
        if response_text.startswith('```'):
            response_text = re.sub(r'^```(?:json)?\s*\n', '', response_text)
            response_text = re.sub(r'\n```\s*$', '', response_text)
        
        quiz_data = json.loads(response_text)
        
        if 'title' not in quiz_data or 'description' not in quiz_data or 'questions' not in quiz_data:
            raise ValueError("Invalid quiz structure: missing required fields")
        
        if len(quiz_data['questions']) != 10:
            raise ValueError(f"Expected 10 questions, got {len(quiz_data['questions'])}")
        
        for i, question in enumerate(quiz_data['questions']):
            if 'question_title' not in question or 'question_options' not in question or 'answer' not in question:
                raise ValueError(f"Question {i+1} has invalid structure")
            
            if len(question['question_options']) != 4:
                raise ValueError(f"Question {i+1} must have exactly 4 options")
        
        return quiz_data
        
    except json.JSONDecodeError as e:
        raise QuizGenerationError(f"Failed to parse JSON from Gemini response: {str(e)}")
    except ValueError as e:
        raise QuizGenerationError(f"Invalid quiz data: {str(e)}")
    except Exception as e:
        raise QuizGenerationError(f"Failed to generate quiz: {str(e)}")


def cleanup_temp_file(file_path: str) -> None:
    """Delete temporary file."""
    
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {file_path}: {str(e)}")
