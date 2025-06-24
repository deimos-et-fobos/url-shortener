import logging
import redis
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('shortener')

class ShortenerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortener'

    def ready(self):
        logger.info(f"Server started in {settings.ENVIRONMENT.upper()} mode")
        if settings.DEBUG:
            logger.info(f"Server started in DEBUG mode")
        if settings.DEBUG and settings.ENVIRONMENT == 'production':
            logger.warning(f"Server is in DEBUG mode during PRODUCTION")
        
        logger.info(f"Database Engine: {settings.DATABASES.get('default').get('ENGINE')}")
        
        if not settings.USE_CACHE:
            logger.warning("USE_CACHE=False: Rate Limiter will not have any effect")
        else:
            try:
                r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
                r.ping()
                logger.info("Redis connection OK")
            except Exception as e:
                logger.error(f"Error connecting to Redis: {e}")