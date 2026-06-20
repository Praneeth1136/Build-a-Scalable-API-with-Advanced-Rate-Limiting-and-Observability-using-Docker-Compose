import os
import time
import logging
from fastapi import Request, Response, HTTPException, status
import redis

# Configure Redis client
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

logger = logging.getLogger("api")

class RateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def __call__(self, request: Request, response: Response):
        # Identify client by IP
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        
        now = time.time()
        
        try:
            # Token Bucket Algorithm via Redis Pipeline
            pipe = r.pipeline()
            pipe.hgetall(key)
            results = pipe.execute()
            
            bucket = results[0] if results else {}
            
            tokens = float(bucket.get("tokens", self.capacity))
            last_refill = float(bucket.get("last_refill", now))
            
            # Calculate tokens to add
            elapsed = now - last_refill
            new_tokens = elapsed * self.refill_rate
            
            tokens = min(self.capacity, tokens + new_tokens)
            
            if tokens >= 1:
                tokens -= 1
                # Save state
                pipe = r.pipeline()
                pipe.hset(key, mapping={"tokens": tokens, "last_refill": now})
                pipe.expire(key, int(self.capacity / self.refill_rate) + 2) # TTL to clean up old keys
                pipe.execute()
                
                # Add headers for successful requests
                reset_time = int(now + (1.0 / self.refill_rate) if tokens < 1 else now)
                response.headers["X-RateLimit-Limit"] = str(self.capacity)
                response.headers["X-RateLimit-Remaining"] = str(int(tokens))
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                
                return True
            else:
                reset_time = int(now + ((1 - tokens) / self.refill_rate))
                logger.warning(f"Rate limit exceeded for {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too Many Requests",
                    headers={
                        "X-RateLimit-Limit": str(self.capacity),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                    }
                )
        except redis.RedisError as e:
            # Fallback if Redis is down, allow request but log error
            logger.error(f"Redis error in rate limiter: {e}")
            return True

# Create a singleton instance based on env vars
capacity = int(os.getenv("RATE_LIMIT_CAPACITY", "10"))
refill_rate = float(os.getenv("RATE_LIMIT_REFILL_RATE", "1"))
rate_limiter = RateLimiter(capacity=capacity, refill_rate=refill_rate)
