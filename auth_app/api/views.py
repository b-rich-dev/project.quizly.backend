from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {'detail': "User created successfully."}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class TestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "This is a test endpoint."}, status=status.HTTP_200_OK)   
    

class CookieLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get('refresh')
        access_token = response.data.get('access')
        user_data = response.data.get('user')
        
        response.set_cookie(
            key='access', 
            value=access_token, 
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        response.set_cookie(
            key='refresh', 
            value=refresh_token, 
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        response.data = {'detail': "Login successfully!", 'user': user_data}
        
        return response
    

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        
        if refresh_token is None:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={'refresh': refresh_token})
        
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'detail': 'Invalid refresh token!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get('access')
        
        response = Response({'detail': 'Token refreshed'})
        response.set_cookie(
            key='access', 
            value=access_token, 
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        return response
    
    
class LogoutView(APIView):
    """API view for user logout."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        
        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        response.delete_cookie('access', samesite='Lax')
        response.delete_cookie('refresh', samesite='Lax')
        return response
    