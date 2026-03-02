from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from quizzes_app.models import Quiz
from .serializers import QuizCreateSerializer, QuizSerializer, QuizDetailSerializer
from .permissions import IsOwner


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
            
            quiz_serializer = QuizDetailSerializer(quiz)
            
            return Response(quiz_serializer.data, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_object(self, pk):
        """Helper method to get quiz object."""
        try:
            quiz = Quiz.objects.prefetch_related('questions').get(pk=pk)
            self.check_object_permissions(self.request, quiz)
            return quiz
        except Quiz.DoesNotExist:
            return None
    
    def get(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """Update quiz title and/or description."""
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Only allow updating title and description
        allowed_fields = {'title', 'description'}
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        if not update_data:
            return Response({"detail": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)
        
        for field, value in update_data.items():
            setattr(quiz, field, value)
        
        quiz.save()
        
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Delete a quiz and all its questions."""
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)