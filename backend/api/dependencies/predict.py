# dependencies/predictor.py

from backend.services import AsyncWeatherPredictorV1, AsyncWeatherPredictorV2
from backend.api.dependencies.redis import get_redis
from redis.asyncio import Redis
from fastapi import Depends

async def get_predictor_v1(redis: Redis = Depends(get_redis)) -> AsyncWeatherPredictorV1:
    return AsyncWeatherPredictorV1(redis)

async def get_predictor_v2(redis: Redis = Depends(get_redis)) -> AsyncWeatherPredictorV2:
    return AsyncWeatherPredictorV2(redis)