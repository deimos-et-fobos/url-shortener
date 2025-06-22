from django.urls import path, re_path
from .views import Redirect, CreateShortURL

app_name = "shortener.api"
urlpatterns = [
    path('api/shortener/', CreateShortURL.as_view(), name='create-short-url'),   
    re_path(r'^(?P<short_url>[a-zA-Z0-9]+)$', Redirect.as_view(), name='redirect'),    
]