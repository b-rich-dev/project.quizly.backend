from rest_framework import serializers
from django.conf import settings
from quizzes_app.models import Quiz, Question
from .utils import (
    validate_youtube_url,
    download_youtube_audio,
    transcribe_audio,
    generate_quiz_from_transcript,
    cleanup_temp_file,
    YouTubeDownloadError,
    TranscriptionError,
    QuizGenerationError,
)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model for GET requests (without timestamps)"""
    
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']
        read_only_fields = fields


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for Question model for POST responses (with timestamps)"""
    
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']
        read_only_fields = fields


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model for GET requests (without timestamps in questions)"""
    
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
        read_only_fields = fields


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model for POST responses (with timestamps in questions)"""
    
    questions = QuestionDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
        read_only_fields = fields


class QuizCreateSerializer(serializers.Serializer):
    """Serializer for creating a quiz from YouTube URL"""
    
    url = serializers.URLField(required=True, help_text="YouTube video URL")
    
    def validate_url(self, value):
        if not validate_youtube_url(value):
            raise serializers.ValidationError("Invalid YouTube URL. Please provide a valid YouTube video URL.")
        return value
    
    def create(self, validated_data):
        """
        Create a quiz from YouTube URL by:
        1. Downloading audio
        2. Transcribing with Whisper
        3. Generating quiz with Gemini
        4. Saving to database
        """
        video_url = validated_data['url']
        temp_audio_path = None
        
        try:
            temp_audio_path = download_youtube_audio(video_url)
            
            transcript = transcribe_audio(temp_audio_path)
            
            quiz_data = generate_quiz_from_transcript(transcript, settings.GEMINI_API_KEY)
            
            user = self.context['request'].user
            quiz = Quiz.objects.create(
                user=user,
                title=quiz_data['title'],
                description=quiz_data['description'],
                video_url=video_url
            )
            
            for question_data in quiz_data['questions']:
                Question.objects.create(
                    quiz=quiz,
                    question_title=question_data['question_title'],
                    question_options=question_data['question_options'],
                    answer=question_data['answer']
                )
            
            return quiz
            
        except YouTubeDownloadError as e:
            raise serializers.ValidationError(f"YouTube download failed: {str(e)}")
        except TranscriptionError as e:
            raise serializers.ValidationError(f"Transcription failed: {str(e)}")
        except QuizGenerationError as e:
            raise serializers.ValidationError(f"Quiz generation failed: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"An unexpected error occurred: {str(e)}")
        finally:
            if temp_audio_path:
                cleanup_temp_file(temp_audio_path)
