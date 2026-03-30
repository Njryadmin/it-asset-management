"""
Redis-based rate limiter for brute force protection.
"""
import time
from functools import wraps
from fastapi import HTTPException, Request, status
import redis.asyncio as redis
from app.core.config import settings


class RateLimiter:
    """Redis-based sliding window rate limiter."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: redis.Redis = None
    
    async def get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis
    
    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def is_rate_limited(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Check if key is rate limited.
        Returns (is_limited, remaining).
        Uses sliding window counter algorithm.
        """
        r = await self.get_redis()
        now = time.time()
        window_start = now - window
        
        pipe = r.pipeline()
        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current requests in window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiry
        pipe.expire(key, window)
        results = await pipe.execute()
        
        current_count = results[1]
        remaining = max(0, limit - current_count - 1)
        
        if current_count >= limit:
            return True, remaining
        return False, remaining


# Global rate limiter instance
_rate_limiter: RateLimiter = None


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(settings.REDIS_URL)
    return _rate_limiter


async def close_rate_limiter():
    global _rate_limiter
    if _rate_limiter:
        await _rate_limiter.close()
        _rate_limiter = None


def rate_limit(limit: str = "5/minute"):
    """
    Decorator to apply rate limiting to an endpoint.
    limit format: "count/window" where window is a number followed by s/m/h/d
    e.g., "5/minute", "10/5m", "3/1h"
    """
    def parse_limit(limit_str: str) -> tuple[int, int]:
        """Parse limit string into (count, window_seconds).
        
        Supported window formats:
        - "5/minute", "5/minutes" → 5 requests per 60 seconds
        - "10/m"               → 10 requests per 60 seconds
        - "3/1h", "3/hour"    → 3 requests per 3600 seconds
        """
        count_str, window_str = limit_str.split("/")
        count = int(count_str)
        
        # Normalize: strip trailing 's' from words like 'minutes'/'hours'
        normalized = window_str.rstrip("s")  # "minutes" → "minute"
        unit = normalized[-1]
        value_str = normalized[:-1]
        
        if not value_str.isdigit():
            # Full word without trailing s, e.g. "minute" → value=1
            value = 1
            unit = normalized  # use full word as key
        else:
            value = int(value_str)
        
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400, "minute": 60, "hour": 3600, "day": 86400}
        if unit not in multipliers:
            raise ValueError(f"Invalid time unit: {unit}")
        window_seconds = value * multipliers[unit]
        return count, window_seconds
    
    count, window = parse_limit(limit)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                # If no request found, skip rate limiting (shouldn't happen in FastAPI)
                return await func(*args, **kwargs)
            
            # Build rate limit key from IP
            client_ip = request.client.host if request.client else "unknown"
            # Use X-Forwarded-For if behind proxy
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
            
            key = f"rate_limit:login:{client_ip}"
            
            limiter = get_rate_limiter()
            is_limited, remaining = await limiter.is_rate_limited(key, count, window)
            
            if is_limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="登录尝试过于频繁，请稍后再试",
                    headers={"Retry-After": str(window)}
                )
            
            response = await func(*args, **kwargs)
            return response
        
        return wrapper
    return decorator
