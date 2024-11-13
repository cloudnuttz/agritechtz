"""Configure cache backend system used by the application"""

# pylint: disable=import-error

from redis.asyncio import Redis

from agritechtz.settings import get_settings


_settings = get_settings()

redis_url = _settings.redis_backend_url

redis_client = Redis.from_url(redis_url)
