from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase


class LoginLogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword123')
        
    def test_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }    
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['detail'], "Login successfully!")

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
        
    def test_missing_fields_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        
    def test_login_nonexistent_user(self):
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        } 
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
        
    def test_logout(self):
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.cookies.get('access_token').value
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        self.client.cookies['access_token'] = login_response.cookies.get('access_token')
        self.client.cookies['refresh_token'] = login_response.cookies.get('refresh_token')
        
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        self.assertIn('access_token', logout_response.cookies)
        self.assertIn('refresh_token', logout_response.cookies)
        self.assertEqual(logout_response.cookies['access_token'].value, '')
        self.assertEqual(logout_response.cookies['refresh_token'].value, '')
        self.assertEqual(logout_response.cookies['access_token']['max-age'], 0)
        self.assertEqual(logout_response.cookies['refresh_token']['max-age'], 0)
        
        self.assertEqual(logout_response.data['detail'], "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.")
    
    def test_logout_without_authentication(self):
        """Test that logout requires authentication"""
        logout_url = reverse('logout')
        response = self.client.post(logout_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class RefreshTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123', email='testuser@example.com')
        
    def test_refresh_token(self):
        """Test successful token refresh with valid refresh token"""
        # First, log in to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Get the refresh token from cookies
        refresh_token = login_response.cookies.get('refresh_token')
        old_access_token = login_response.cookies.get('access_token').value
        
        # Set the refresh token cookie for the refresh request
        self.client.cookies['refresh_token'] = refresh_token
        
        # Call the refresh endpoint
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, format='json')
        
        # Verify the response
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response.data['detail'], 'Token refreshed')
        self.assertIn('access_token', refresh_response.cookies)
        
        # Verify new access token is different from old one
        new_access_token = refresh_response.cookies.get('access_token').value
        self.assertNotEqual(old_access_token, new_access_token)
        
    def test_refresh_token_without_cookie(self):
        """Test token refresh without refresh token cookie"""
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Refresh token not found.')
        
    def test_refresh_token_invalid(self):
        """Test token refresh with invalid refresh token"""
        # Set an invalid refresh token
        self.client.cookies['refresh_token'] = 'invalid_token_string'
        
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid refresh token!')
        
    def test_refresh_token_after_logout(self):
        """Test that refresh token cannot be used after logout (blacklisted)"""

        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.cookies.get('access_token').value
        refresh_token = login_response.cookies.get('refresh_token')
        
        # Log out (this should blacklist the refresh token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.cookies['access_token'] = login_response.cookies.get('access_token')
        self.client.cookies['refresh_token'] = refresh_token
        
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Try to use the refresh token after logout
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, format='json')
        
        # Should fail because token is blacklisted
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.data['detail'], 'Invalid refresh token!')
        