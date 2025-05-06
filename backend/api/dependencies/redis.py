# dependencies/redis.py

from redis.asyncio import Redis
from redis.asyncio import BlockingConnectionPool
import typing as t
from backend.config import settings  # your settings.py path

redis_db: t.Optional[Redis] = None

async def create_redis_connection() -> Redis:
    pool = BlockingConnectionPool.from_url(
        settings.redis_uri,
        max_connections=settings.REDIS_POOL_SIZE,
        timeout=int(settings.REDIS_POOL_TIMEOUT.total_seconds()),
    )
    db = Redis(connection_pool=pool)
    return db

async def get_redis() -> Redis:
    global redis_db
    if redis_db is None:
        raise RuntimeError("Redis connection not initialized")
    return redis_db

async def close_redis():
    global redis_db
    if redis_db is not None:
        await redis_db.close()
        redis_db = None
