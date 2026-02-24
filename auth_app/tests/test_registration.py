from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123',
            'email': 'testuser@example.com'     
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(User.objects.get().email, 'testuser@example.com')
        self.assertEqual(response.data['detail'], "User created successfully.")

    def test_registration_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'password': 'testpassword123',
            'confirmed_password': 'differentpassword',
            'email': 'testuser2@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_register_duplicate_email(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'confirmed_password': 'newpassword123',
            'email': 'existing@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_register_duplicate_username(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        url = reverse('register')
        data = {
            'username': 'existinguser',
            'password': 'newpassword123',
            'confirmed_password': 'newpassword123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_missing_fields(self):
        url = reverse('register')
        data = {
            'username': 'testuser3',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123',
            'email': ''
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_register_without_email_field(self):
        url = reverse('register')
        data = {
            'username': 'testuser4',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_register_invalid_email_format(self):
        url = reverse('register')
        data = {
            'username': 'testuser5',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123',
            'email': 'notavalidemail'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        