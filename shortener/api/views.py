from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import views, generics, permissions
from shortener.models import ShortURL
from .serializers import ShortURLSerializer
from django.utils import timezone

class CreateShortURL(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShortURLSerializer


class Redirect(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, short_url):
        obj = get_object_or_404(ShortURL, short_url=short_url)
        # Save last access
        obj.last_access = timezone.now()
        obj.save(update_fields=["last_access"])
        return HttpResponseRedirect(redirect_to=obj.long_url)
