import redis
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation using Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limit = 1000  # requests per hour
        self.default_window = 3600  # 1 hour in seconds
    
    async def is_allowed(self, client_ip: str, limit: Optional[int] = None, window: Optional[int] = None) -> bool:
        """Check if request is allowed based on rate limiting"""
        limit = limit or self.default_limit
        window = window or self.default_window
        
        try:
            # Create a sliding window counter
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(f"rate_limit:{client_ip}", 0, window_start)
            
            # Count current requests
            pipe.zcard(f"rate_limit:{client_ip}")
            
            # Add current request
            pipe.zadd(f"rate_limit:{client_ip}", {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(f"rate_limit:{client_ip}", window)
            
            results = pipe.execute()
            current_count = results[1]
            
            return current_count < limit
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request if Redis is down
            return True
    
    async def get_current_count(self, client_ip: str, window: Optional[int] = None) -> int:
        """Get current request count for an IP"""
        window = window or self.default_window
        current_time = int(time.time())
        window_start = current_time - window
        
        try:
            # Remove old entries and count current
            self.redis.zremrangebyscore(f"rate_limit:{client_ip}", 0, window_start)
            return self.redis.zcard(f"rate_limit:{client_ip}")
        except Exception as e:
            logger.error(f"Error getting rate limit count: {e}")
            return 0
    
    async def reset_rate_limit(self, client_ip: str) -> bool:
        """Reset rate limit for an IP"""
        try:
            self.redis.delete(f"rate_limit:{client_ip}")
            return True
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
            return False
