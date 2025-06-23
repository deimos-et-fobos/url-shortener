from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.conf import settings

default_rate_limit = method_decorator(ratelimit(key='ip', rate=settings.RATE_LIMIT, block=True), name='dispatch')