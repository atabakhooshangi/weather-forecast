import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.dependencies import redis

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
async def mock_redis():
    """Mock Redis connection for all tests"""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(redis, "create_redis_connection", AsyncMock())
        m.setattr(redis, "close_redis", AsyncMock())
        yield 