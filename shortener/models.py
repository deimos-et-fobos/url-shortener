from django.db import models

SHORT_URL_MAX_LENGTH = 10
LONG_URL_MAX_LENGTH = 1048

class ShortURL(models.Model):
    short_url = models.CharField(max_length=SHORT_URL_MAX_LENGTH, unique=True)
    url = models.URLField(max_length=LONG_URL_MAX_LENGTH)
    last_access = models.DateTimeField(auto_now=True)   # For cleaning up db
    
    def __str__(self):
        return f"{self.short_url} --> {self.url}"