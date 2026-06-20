import pytest
from httpx import AsyncClient
from ..main import app
import redis
import os

@pytest.fixture(autouse=True)
def flush_redis():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    try:
        r = redis.Redis(host=redis_host, port=redis_port)
        r.flushdb()
    except:
        pass

@pytest.mark.asyncio
async def test_get_status():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/products", json={"name": "Test", "description": "Desc", "price": 10.5})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_products():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/products", json={"name": "Test2", "description": "Desc2", "price": 20.0})
        response = await ac.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] in ["Test", "Test2"]

@pytest.mark.asyncio
async def test_rate_limiter_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/protected-action")
    assert response.status_code == 200
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers

@pytest.mark.asyncio
async def test_rate_limiter_exceed():
    capacity = int(os.getenv("RATE_LIMIT_CAPACITY", "10"))
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Exhaust tokens
        for _ in range(capacity):
            await ac.post("/api/protected-action")
        
        # Next one should fail
        response = await ac.post("/api/protected-action")
        assert response.status_code == 429
        assert "x-ratelimit-limit" in response.headers
        assert response.headers["x-ratelimit-remaining"] == "0"
