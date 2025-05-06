import typing as t
from datetime import timedelta
from redis.asyncio import BlockingConnectionPool, Redis

async def create_redis_connection(
    db_url: str,
    pool_size: int,
    pool_timeout: timedelta,
) -> t.AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    pool = BlockingConnectionPool.from_url(
        db_url,
        max_connections=pool_size,
        timeout=int(pool_timeout.total_seconds()),
    )
    db: Redis = Redis(  # type: ignore[type-arg]
        connection_pool=pool,
    )
    yield db
    await db.close()