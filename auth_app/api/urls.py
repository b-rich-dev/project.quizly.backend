from django.urls import path
from .views import RegisterView, TestView, CookieLoginView, CookieTokenRefreshView, LogoutView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CookieLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    
    path('test/', TestView.as_view(), name='test'),
]