from django.http import JsonResponse
from rest_framework import status

def ratelimit_error_view(request, exception):
    return JsonResponse(
        {"detail": "Too many requests"},
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )