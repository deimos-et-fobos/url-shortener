import random
import string
from .models import ShortURL
from rest_framework import serializers
from django.conf import settings
from .constants import PROTECTED_URLS

BASE62_CHARS = string.ascii_letters + string.digits  # a-zA-Z0-9

class ShortURLGenerationError(Exception):
    pass

# Completly random short url
def random_short_url():
    return ''.join(random.choices(BASE62_CHARS, k=settings.SHORT_URL_LENGTH))

# Short url build using Timestamp + id
# def ts_id_short_url(length=8):
#     return ''

def check_short_url(short_url):
    if short_url in PROTECTED_URLS:
        raise serializers.ValidationError("Url not available.")
    if ShortURL.objects.filter(short_url=short_url).exists():
        raise serializers.ValidationError("Url not available.")  
    pass
    
def generate_short_url(custom_short=None):
    if custom_short:
        check_short_url(custom_short)
        return custom_short
    
    for _ in range(10):
        short_url = random_short_url()
        try:
            check_short_url(short_url)
            return short_url
        except serializers.ValidationError:
            continue
        
    raise ShortURLGenerationError("Couldn't create a unique short url")