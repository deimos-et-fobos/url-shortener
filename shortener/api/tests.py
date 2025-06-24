import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from .serializers import ShortURLSerializer
from shortener.models import ShortURL, SHORT_URL_MAX_LENGTH
from shortener.utils import generate_short_url, ShortURLGenerationError
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from time import sleep

User = get_user_model()

TEST_SHORT_URL ="abcd1234"
TEST_URL = "https://google.com"

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_client():
    user = User.objects.create_user(email="testuser@gmail.com", password="testpass123!")
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client, user

@pytest.fixture
def short_url_obj():
    return ShortURL.objects.create(
        short_url=TEST_SHORT_URL,
        url=TEST_URL
    )
    
@pytest.mark.django_db
class TestRedirectView:
    def test_redirects(self, client, short_url_obj):
        url = reverse('shortener.api:redirect', kwargs={'short_url': short_url_obj.short_url})
        response = client.get(url)
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == short_url_obj.url
    
    def test_updates_last_access(self, client, mocker, short_url_obj):
        last_access = short_url_obj.last_access
        sleep(1)
        # Mock cache.get() to avoid caching the response 
        mock = mocker.patch("shortener.api.views.cache.get", side_effect=[None])
        url = reverse('shortener.api:redirect', kwargs={'short_url': short_url_obj.short_url})
        response = client.get(url)
        short_url_obj.refresh_from_db()
        assert short_url_obj.last_access > last_access


@pytest.mark.django_db
class TestShortURLValidations:
    def test_short_url_only_alphanumeric(self):
        data = { "url": TEST_URL }
        data["short_url"] = TEST_SHORT_URL
        serializer = ShortURLSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        data["short_url"] = "abcd_!@#"
        serializer = ShortURLSerializer(data=data)
        assert not serializer.is_valid()
        assert "short_url" in serializer.errors
        assert any("only numbers and letters" in e for e in serializer.errors["short_url"])

    def test_short_url_max_length(self):
        data = { "url": TEST_URL }
        data["short_url"] = "a" * SHORT_URL_MAX_LENGTH
        serializer = ShortURLSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        data["short_url"] = "a" * (SHORT_URL_MAX_LENGTH + 1)
        serializer = ShortURLSerializer(data=data)
        assert not serializer.is_valid()
        assert "short_url" in serializer.errors
        assert any(f"at most {SHORT_URL_MAX_LENGTH} characters" in e for e in serializer.errors["short_url"])

    def test_short_url_unique(self, short_url_obj):
        serializer = ShortURLSerializer(data={"short_url": TEST_SHORT_URL, "url": TEST_URL})
        assert not serializer.is_valid()
        assert "short_url" in serializer.errors
        assert any("not available" in e for e in serializer.errors["short_url"])


@pytest.mark.django_db
class TestDuplicateShortURL:
    def test_generate_new_short_url_if_duplicate(self, mocker):
        ShortURL.objects.create(short_url=TEST_SHORT_URL, url=TEST_URL)
        # Mock random_short_url to return TEST_URL twice, and then "1234abcd"
        mock_random = mocker.patch("shortener.utils.random_short_url", side_effect=[TEST_SHORT_URL, TEST_SHORT_URL, "UNIQUE"])
        result = generate_short_url(None)
        assert result == "UNIQUE"
        assert mock_random.call_count == 3
        
    def test_couldnt_generate_unique_short_url(self, mocker):
        ShortURL.objects.create(short_url=TEST_SHORT_URL, url=TEST_URL)
        mock_random_short_url = mocker.patch("shortener.utils.random_short_url", side_effect=[TEST_SHORT_URL] * 10)
        with pytest.raises(ShortURLGenerationError, match="Couldn't create a unique short url"):
            generate_short_url(None)
        assert mock_random_short_url.call_count == 10
        

@pytest.mark.django_db
class TestCreateShortURL:
    def test_user_is_authenticated(self, authenticated_client):
        client, user = authenticated_client
        url = reverse('shortener.api:create-short-url')
        response = client.post(url, {"url": TEST_URL})
        assert response.status_code == status.HTTP_201_CREATED
        
    def test_user_is_not_authenticated(self, client):
        url = reverse('shortener.api:create-short-url')
        response = client.post(url, {"url": TEST_URL})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRedirectCache:
    def test_redirect_cache(self, client, short_url_obj):
        # Skip test if not using cache
        if not settings.USE_CACHE:
            pytest.skip("Cache disabled, skipping test...")
            
        # get key and clean cache
        cache_key = f"shorturl:{short_url_obj.short_url}"
        cache.delete(cache_key)

        # 1st request, empty cache, save cache and redirect 
        url = reverse('shortener.api:redirect', kwargs={'short_url': short_url_obj.short_url})
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == short_url_obj.url

        # chech if cached value is correct
        assert cache.get(cache_key) == short_url_obj.url

        # 2nd request, get cached url and redirect
        with patch('shortener.api.views.get_object_or_404') as mock_get:
            response = client.get(url)
            assert response.status_code == 302
            assert response.url == short_url_obj.url
            mock_get.assert_not_called()