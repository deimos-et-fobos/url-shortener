from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import views, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from shortener.models import ShortURL
from .serializers import ShortURLSerializer
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
from config.utils import default_rate_limit

@default_rate_limit
class CreateShortURL(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShortURLSerializer

    @swagger_auto_schema(
        operation_id="create_short_url",
        operation_description="Create a new short URL",
        tags=["Shortener"],
        security=[{'Bearer': []}],
        responses={
            201: openapi.Response(
                description="Short URL created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "url": openapi.Schema(type=openapi.TYPE_STRING, example="https://www.google.com"),
                        "short_url": openapi.Schema(type=openapi.TYPE_STRING, example="as2dD37F")
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@default_rate_limit
class Redirect(views.APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_id="redirect_to_URL",
        operation_description="Redirect to the original URL: short URL --> URL",
        tags=["Shortener"],
        responses={
            302: openapi.Response(description="Redirected to the original URL"),
            404: openapi.Response(description="Short URL not found"),
        }
    )
    def get(self, request, short_url):
        cache_key = f"shorturl:{short_url}"
        # Get value from cache
        url = cache.get(cache_key)

        if url:
            # If it's in cache renew TTL
            cache.set(cache_key, url, timeout=3600)
        else:
            obj = get_object_or_404(ShortURL, short_url=short_url)   
            url = obj.url
            # Save in the Cache
            cache.set(cache_key, url, timeout=3600)  # 1hs
            # Save last access
            obj.last_access = timezone.now()
            obj.save(update_fields=["last_access"])
            
        return HttpResponseRedirect(redirect_to=url)
