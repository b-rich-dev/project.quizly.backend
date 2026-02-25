from django.urls import path
from .views import QuizView

urlpatterns = [
    path('quizzes/', QuizView.as_view(), name='quizzes'),
]