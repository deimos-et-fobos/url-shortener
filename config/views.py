import logging
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger('shortener')

def ratelimit_error_view(request, exception):
    ip = request.META.get('REMOTE_ADDR')
    logger.warning(f'Too many request from ip: {ip} | user: {request.user}')
    return JsonResponse(
        {"detail": "Too many requests"},
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )