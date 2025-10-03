import asyncio
import logging
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from config import get_settings

logger = logging.getLogger(__name__)

async def init_rate_limiter():
    settings = get_settings()
    try:
        redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis)
        logger.info("Rate limiter initialized with Redis.")
    except Exception as e:
        logger.warning("Rate limiter not active (Redis issue): %s", e)
