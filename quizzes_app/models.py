from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(required=True)
    

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField(choices=[('Option A', 'Option A'), ('Option B', 'Option B'), ('Option C', 'Option C'), ('Option D', 'Option D')])
    answer = models.CharField(max_length=20, choices=[('Option A', 'Option A'), ('Option B', 'Option B'), ('Option C', 'Option C'), ('Option D', 'Option D')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
    