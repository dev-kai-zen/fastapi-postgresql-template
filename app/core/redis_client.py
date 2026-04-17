from collections.abc import Generator

import redis

from .config import get_settings


def get_redis() -> Generator[redis.Redis, None, None]:
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        client.close()
