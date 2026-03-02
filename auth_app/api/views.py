from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    API view for user registration.
    Allows any user to create a new account with username, email, and password.
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {'detail': "User created successfully."}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@method_decorator(csrf_exempt, name='dispatch')
class CookieLoginView(TokenObtainPairView):
    """
    API view for user login with JWT tokens stored in HTTP-only cookies.
    Returns access and refresh tokens in secure cookies along with user data.
    """
    
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
    

@method_decorator(csrf_exempt, name='dispatch')
class CookieTokenRefreshView(TokenRefreshView):
    """
    API view for refreshing JWT access tokens using refresh token from cookies.
    Validates the refresh token and issues a new access token in a secure cookie.
    """
    
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
    

@method_decorator(csrf_exempt, name='dispatch')    
class LogoutView(APIView):
    """
    API view for user logout.
    Blacklists the refresh token and deletes authentication cookies for authenticated users.
    """
    
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
    