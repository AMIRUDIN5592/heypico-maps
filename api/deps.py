from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from config import get_settings  

def limiter_dep():
    settings = get_settings()
    return RateLimiter(times=settings.RATE_LIMIT_PER_MINUTE, seconds=60)

def get_rate_limiter(limit=Depends(limiter_dep)):
    # dummy dependency, hanya untuk inject limiter ke route
    return limit
