import pytest
import httpx
from fastapi import FastAPI

from src.constants import MAX_BATCH_SIZE, MAX_K, MIN_K
from src.main import app


@pytest.mark.asyncio
async def test_add_batch_endpoint_valid():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/add_batch/", json={"symbol": "AAPL", "values": [1.0, 2.0, 3.0]}
        )
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_batch_endpoint_invalid_batch_size():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/add_batch/", json={"symbol": "GOOGL", "values": [1.0] * (MAX_BATCH_SIZE + 1)}
        )
        assert response.status_code == 422
        assert "values" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_get_stats_endpoint_valid():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        # Setup
        await async_client.post("/add_batch/", json={"symbol": "AAPL", "values": [1.0, 2.0, 3.0]})

        response = await async_client.get("/stats/AAPL/1")
        assert response.status_code == 200
        data = response.json()
        assert data["min"] == 1.0
        assert data["max"] == 3.0


@pytest.mark.asyncio
async def test_get_stats_endpoint_invalid_symbol():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get("/stats/NOSUCH/1")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stats_endpoint_invalid_k_too_high():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(f"/stats/AAPL/{MAX_K + 1}")
        assert response.status_code == 422
        assert (
            f"Window size exponent (k={MAX_K + 1}) must be between {MIN_K} and {MAX_K}"
            in response.json()["detail"]
        )


@pytest.mark.asyncio
async def test_get_stats_endpoint_invalid_k_too_low():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(f"/stats/AAPL/{MIN_K - 1}")
        assert response.status_code == 422
        assert (
            f"Window size exponent (k={MIN_K - 1}) must be between {MIN_K} and {MAX_K}"
            in response.json()["detail"]
        )


@pytest.mark.asyncio
async def test_get_stats_endpoint_invalid_k_negative():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get("/stats/AAPL/-1")
        assert response.status_code == 422
        assert response.json()["detail"] == "Window size exponent (k=-1) must be between 1 and 8"
