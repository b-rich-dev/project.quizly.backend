from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from quizzes_app.models import Quiz
from .serializers import QuizCreateSerializer, QuizSerializer


class QuizView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        quizzes = Quiz.objects.filter(user=request.user.id)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new quiz from YouTube URL."""
        
        serializer = QuizCreateSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quiz = serializer.save()
            quiz = Quiz.objects.prefetch_related('questions').get(pk=quiz.pk)
            
            quiz_serializer = QuizSerializer(quiz)
            
            return Response(quiz_serializer.data, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
