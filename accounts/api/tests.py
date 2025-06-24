import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest.mock import patch

User = get_user_model()

@pytest.fixture
def client():
    return APIClient()
  
@pytest.fixture
def test_user():
    return User.objects.create_user(email="testuser@gmail.com", password="testpass123!")

@pytest.mark.django_db
@patch('django_ratelimit.decorators.ratelimit', lambda *args, **kwargs: lambda x: x) # Disable Rate-Limit in tests
class TestRegister:
    def test_register_user_success(self, client):
        url = reverse('accounts.api:register')
        data = {
            "email": "newuser@gmail.com",
            "password1": "testpass123!",
            "password2": "testpass123!"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@gmail.com").exists()

    def test_register_passwords_dont_match(self, client):
        url = reverse('accounts.api:register')
        data = {
            "email": "newuser@gmail.com",
            "password1": "testpass123!",
            "password2": "testpass123"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password2" in response.data


@pytest.mark.django_db
@patch('django_ratelimit.decorators.ratelimit', lambda *args, **kwargs: lambda x: x) # Disable Rate-Limit in tests
class TestLogin:
    def test_login_success(self, client, test_user):
        url = reverse('accounts.api:login')
        data = {
            "email": test_user.email,
            "password": "testpass123!"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_user(self, client):
        url = reverse('accounts.api:login')
        data = {
            "email": "testuser@hotmail.com",
            "password": "wrongpass"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_login_invalid_password(self, client):
        url = reverse('accounts.api:login')
        data = {
            "email": "testuser@gmail.com",
            "password": "wrongpass"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@patch('django_ratelimit.decorators.ratelimit', lambda *args, **kwargs: lambda x: x) # Disable Rate-Limit in tests
class TestRefreshToken:
    def test_token_refresh(self, client, test_user):
        login_url = reverse('accounts.api:login')
        login_response = client.post(login_url, {"email": test_user.email, "password": "testpass123!"})
        refresh_token = login_response.data["refresh"]

        refresh_url = reverse('accounts.api:token-refresh')
        response = client.post(refresh_url, {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
@patch('django_ratelimit.decorators.ratelimit', lambda *args, **kwargs: lambda x: x) # Disable Rate-Limit in tests
class TestLogout:
    def test_logout_success(self, client, test_user):
        login_url = reverse('accounts.api:login')
        login_response = client.post(login_url, {"email": test_user.email, "password": "testpass123!"})
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        logout_url = reverse('accounts.api:logout')
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post(logout_url, {"refresh": refresh})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Logout successful."
        
    def test_logout_bearer_not_provided(self, client, test_user):
        login_url = reverse('accounts.api:login')
        login_response = client.post(login_url, {"email": test_user.email, "password": "testpass123!"})
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        logout_url = reverse('accounts.api:logout')
        response = client.post(logout_url, {"refresh": refresh})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Authentication credentials were not provided."
    
    def test_logout_wrong_bearer_token(self, client, test_user):
        login_url = reverse('accounts.api:login')
        login_response = client.post(login_url, {"email": test_user.email, "password": "testpass123!"})
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        logout_url = reverse('accounts.api:logout')
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh}")
        response = client.post(logout_url, {"refresh": refresh})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Given token not valid for any token type"
    
    def test_logout_refresh_not_provided(self, client, test_user):
        login_url = reverse('accounts.api:login')
        login_response = client.post(login_url, {"email": test_user.email, "password": "testpass123!"})
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        logout_url = reverse('accounts.api:logout')
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post(logout_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token required."
