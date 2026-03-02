from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from unittest.mock import patch
from quizzes_app.models import Quiz, Question


class QuizDetailTests(APITestCase):
    """Tests for GET, PATCH and DELETE /api/quizzes/<pk>/ endpoints"""
    
    def setUp(self):
        """Set up test users and quizzes"""
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
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
        
        self.quiz2 = Quiz.objects.create(
            user=self.user2,
            title='JavaScript Basics',
            description='Learn JavaScript',
            video_url='https://www.youtube.com/watch?v=test2'
        )
    
    def test_get_quiz_detail_success(self):
        """Test successful retrieval of a specific quiz by owner"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.quiz1.pk)
        self.assertEqual(response.data['title'], 'Python Basics')
        self.assertEqual(response.data['description'], 'Learn Python fundamentals')
        self.assertEqual(response.data['video_url'], 'https://www.youtube.com/watch?v=test1')
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
        self.assertEqual(len(response.data['questions']), 1)
        
        question = response.data['questions'][0]
        self.assertEqual(question['question_title'], 'What is Python?')
        self.assertIn('id', question)
        self.assertIn('question_options', question)
        self.assertIn('answer', question)
        self.assertNotIn('created_at', question)
        self.assertNotIn('updated_at', question)
    
    def test_get_quiz_detail_unauthorized_user(self):
        """Test that user cannot access another user's quiz (403)"""
        
        self.client.force_authenticate(user=self.user2)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_quiz_detail_not_found(self):
        """Test retrieval of non-existent quiz (404)"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_quiz_detail_unauthenticated(self):
        """Test that unauthenticated user cannot access quiz (401)"""
        
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patch_quiz_success(self):
        """Test successful quiz update by owner"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        data = {
            'title': 'Updated Python Basics',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Python Basics')
        self.assertEqual(response.data['description'], 'Updated description')
        
        self.quiz1.refresh_from_db()
        self.assertEqual(self.quiz1.title, 'Updated Python Basics')
    
    def test_patch_quiz_title_only(self):
        """Test updating only title"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        data = {'title': 'New Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.assertEqual(response.data['description'], 'Learn Python fundamentals')
    
    def test_patch_quiz_returns_complete_quiz_with_questions(self):
        """Test that PATCH response includes complete quiz with questions"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        data = {'title': 'Updated Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('description', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
        self.assertIn('video_url', response.data)
        self.assertIn('questions', response.data)
        
        self.assertEqual(len(response.data['questions']), 1)
        question = response.data['questions'][0]
        self.assertIn('id', question)
        self.assertIn('question_title', question)
        self.assertIn('question_options', question)
        self.assertIn('answer', question)
        self.assertNotIn('created_at', question)
        self.assertNotIn('updated_at', question)
    
    def test_patch_quiz_unauthorized_user(self):
        """Test that user cannot update another user's quiz"""
        
        self.client.force_authenticate(user=self.user2)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        data = {'title': 'Hacked Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.quiz1.refresh_from_db()
        self.assertEqual(self.quiz1.title, 'Python Basics')
    
    def test_patch_quiz_not_found(self):
        """Test updating non-existent quiz"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        data = {'title': 'New Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_patch_quiz_no_valid_fields(self):
        """Test updating with no valid fields"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        data = {'invalid_field': 'value'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_patch_quiz_cannot_change_video_url(self):
        """Test that video_url cannot be changed"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        original_url = self.quiz1.video_url
        data = {
            'title': 'New Title',
            'video_url': 'https://www.youtube.com/watch?v=hacked'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz1.refresh_from_db()
        self.assertEqual(self.quiz1.video_url, original_url)
    
    def test_delete_quiz_success(self):
        """Test successful quiz deletion by owner"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(response.data, None)

        self.assertEqual(Quiz.objects.filter(pk=self.quiz1.pk).count(), 0)
        self.assertEqual(Question.objects.filter(quiz=self.quiz1.pk).count(), 0)
    
    def test_delete_quiz_unauthorized_user(self):
        """Test that user cannot delete another user's quiz"""
        
        self.client.force_authenticate(user=self.user2)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Quiz.objects.filter(pk=self.quiz1.pk).count(), 1)
    
    def test_delete_quiz_not_found(self):
        """Test deleting non-existent quiz"""
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_quiz_unauthenticated(self):
        """Test that unauthenticated user cannot delete quiz"""
        
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Quiz.objects.filter(pk=self.quiz1.pk).count(), 1)
