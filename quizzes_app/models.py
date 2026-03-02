from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Quiz model representing a quiz created by a user.
    Contains title, description, video URL, and related questions.
    """
    
    user = models.ForeignKey(User, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField()
    

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Question model representing a quiz question.
    Contains question title, multiple choice options (JSON), correct answer, and belongs to a quiz.
    """
    
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
    