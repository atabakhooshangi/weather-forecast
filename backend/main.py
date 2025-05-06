from contextlib import asynccontextmanager
from backend.api.api_router import api_router
from backend.config import settings
from random import randint
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.api.dependencies import redis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    print("🔌 Connecting to Redis...")
    redis.redis_db = await redis.create_redis_connection()
    FastAPICache.init(RedisBackend(redis.redis_db), prefix="forecast_cache")
    yield
    print("🛑 Closing Redis connection...")
    await redis.close_redis()

app = FastAPI(
    lifespan=lifespan,
    title="Library",
    docs_url="/api/docs")

app.add_middleware(
    SessionMiddleware,
    secret_key=f"{randint(1000, 4000)}-secret-string-{randint(1000, 4000)}",

)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:3000",
        "http://frontend:5173"  # Docker service name
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(api_router)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=settings.SERVER_PORT,
        reload=settings.RELOAD
    )
