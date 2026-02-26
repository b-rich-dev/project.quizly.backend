from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.models import Quiz, Question


class QuizListTests(APITestCase):
    """Tests for GET /api/quizzes/ endpoint"""
    
    def setUp(self):
        """Set up test users and quizzes"""
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
        # Create quizzes for user1
        self.quiz1 = Quiz.objects.create(
            user=self.user1,
            title='Python Basics',
            description='Learn Python fundamentals',
            video_url='https://www.youtube.com/watch?v=test1'
        )
        Question.objects.create(
            quiz=self.quiz1,
            question_title='What is Python?',
            question_options=['A programming language', 'A snake', 'A framework'],
            answer='A programming language'
        )
        
        # Create quiz for user2
        self.quiz2 = Quiz.objects.create(
            user=self.user2,
            title='JavaScript Basics',
            description='Learn JavaScript',
            video_url='https://www.youtube.com/watch?v=test2'
        )
    
    def test_get_quizzes_authenticated(self):
        """Test that authenticated user can get their quizzes"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('quizzes')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Basics')
        self.assertEqual(len(response.data[0]['questions']), 1)
    
    def test_get_quizzes_unauthenticated(self):
        """Test that unauthenticated user cannot get quizzes"""
        url = reverse('quizzes')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_quizzes_empty_list(self):
        """Test that user with no quizzes gets empty list"""
        user3 = User.objects.create_user(username='user3', password='testpass123')
        self.client.force_authenticate(user=user3)
        url = reverse('quizzes')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class QuizCreateTests(APITestCase):
    """Tests for POST /api/quizzes/ endpoint"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.url = reverse('quizzes')
        self.valid_youtube_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        
        # Mock quiz data that would be generated
        self.mock_quiz_data = {
            'title': 'Test Quiz',
            'description': 'A quiz about testing',
            'questions': [
                {
                    'question_title': 'What is testing?',
                    'question_options': ['Verification', 'Guessing', 'Hoping'],
                    'answer': 'Verification'
                },
                {
                    'question_title': 'Why test?',
                    'question_options': ['Quality', 'Fun', 'Required'],
                    'answer': 'Quality'
                }
            ]
        }
    
    @patch('quizzes_app.api.serializers.cleanup_temp_file')
    @patch('quizzes_app.api.serializers.generate_quiz_from_transcript')
    @patch('quizzes_app.api.serializers.transcribe_audio')
    @patch('quizzes_app.api.serializers.download_youtube_audio')
    @patch('quizzes_app.api.serializers.validate_youtube_url')
    def test_create_quiz_success(self, mock_validate, mock_download, mock_transcribe, mock_generate, mock_cleanup):
        """Test successful quiz creation from YouTube URL"""
        # Setup mocks
        mock_validate.return_value = True
        mock_download.return_value = '/tmp/test_audio.mp3'
        mock_transcribe.return_value = 'This is a test transcript'
        mock_generate.return_value = self.mock_quiz_data
        
        self.client.force_authenticate(user=self.user)
        data = {'url': self.valid_youtube_url}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Quiz')
        self.assertEqual(response.data['description'], 'A quiz about testing')
        self.assertEqual(response.data['video_url'], self.valid_youtube_url)
        self.assertEqual(len(response.data['questions']), 2)
        self.assertEqual(response.data['questions'][0]['question_title'], 'What is testing?')
        
        # Verify quiz was saved to database
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 2)
        
        # Verify mocks were called
        mock_validate.assert_called_once_with(self.valid_youtube_url)
        mock_download.assert_called_once_with(self.valid_youtube_url)
        mock_transcribe.assert_called_once_with('/tmp/test_audio.mp3')
        mock_generate.assert_called_once()
        mock_cleanup.assert_called_once_with('/tmp/test_audio.mp3')
    
    def test_create_quiz_unauthenticated(self):
        """Test that unauthenticated user cannot create quiz"""
        data = {'url': self.valid_youtube_url}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('quizzes_app.api.serializers.validate_youtube_url')
    def test_create_quiz_invalid_url(self, mock_validate):
        """Test quiz creation with invalid YouTube URL"""
        mock_validate.return_value = False
        
        self.client.force_authenticate(user=self.user)
        data = {'url': 'https://invalid-url.com'}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)
    
    def test_create_quiz_missing_url(self):
        """Test quiz creation without URL"""
        self.client.force_authenticate(user=self.user)
        data = {}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)
    
    @patch('quizzes_app.api.serializers.download_youtube_audio')
    @patch('quizzes_app.api.serializers.validate_youtube_url')
    def test_create_quiz_youtube_download_error(self, mock_validate, mock_download):
        """Test quiz creation when YouTube download fails"""
        from quizzes_app.api.utils import YouTubeDownloadError
        
        mock_validate.return_value = True
        mock_download.side_effect = YouTubeDownloadError("Video not available")
        
        self.client.force_authenticate(user=self.user)
        data = {'url': self.valid_youtube_url}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('YouTube download failed', str(response.data))
    
    @patch('quizzes_app.api.serializers.cleanup_temp_file')
    @patch('quizzes_app.api.serializers.transcribe_audio')
    @patch('quizzes_app.api.serializers.download_youtube_audio')
    @patch('quizzes_app.api.serializers.validate_youtube_url')
    def test_create_quiz_transcription_error(self, mock_validate, mock_download, mock_transcribe, mock_cleanup):
        """Test quiz creation when transcription fails"""
        from quizzes_app.api.utils import TranscriptionError
        
        mock_validate.return_value = True
        mock_download.return_value = '/tmp/test_audio.mp3'
        mock_transcribe.side_effect = TranscriptionError("Audio file corrupted")
        
        self.client.force_authenticate(user=self.user)
        data = {'url': self.valid_youtube_url}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transcription failed', str(response.data))
        mock_cleanup.assert_called_once_with('/tmp/test_audio.mp3')
    
    @patch('quizzes_app.api.serializers.cleanup_temp_file')
    @patch('quizzes_app.api.serializers.generate_quiz_from_transcript')
    @patch('quizzes_app.api.serializers.transcribe_audio')
    @patch('quizzes_app.api.serializers.download_youtube_audio')
    @patch('quizzes_app.api.serializers.validate_youtube_url')
    def test_create_quiz_generation_error(self, mock_validate, mock_download, mock_transcribe, mock_generate, mock_cleanup):
        """Test quiz creation when quiz generation fails"""
        from quizzes_app.api.utils import QuizGenerationError
        
        mock_validate.return_value = True
        mock_download.return_value = '/tmp/test_audio.mp3'
        mock_transcribe.return_value = 'Test transcript'
        mock_generate.side_effect = QuizGenerationError("Gemini API error")
        
        self.client.force_authenticate(user=self.user)
        data = {'url': self.valid_youtube_url}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Quiz generation failed', str(response.data))
        mock_cleanup.assert_called_once_with('/tmp/test_audio.mp3')
