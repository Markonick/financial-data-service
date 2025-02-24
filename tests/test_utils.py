import pytest

from src.utils import time_execution


@pytest.mark.asyncio
async def test_time_execution_basic():
    @time_execution
    async def sample_function():
        return {
            "request_count": 10,
            "total_time": 1000.0,  # microseconds
            "total_trades": 100,
        }

    result = await sample_function()

    # Original function's return values should be preserved
    assert result["request_count"] == 10
    assert result["total_time"] == 1000.0
    assert result["total_trades"] == 100


@pytest.mark.asyncio
async def test_time_execution_empty_result():
    @time_execution
    async def empty_function():
        return {"request_count": 0, "total_time": 0.0, "total_trades": 0}

    # Should handle zero values gracefully
    result = await empty_function()
    assert isinstance(result, dict)
    assert result["request_count"] == 0
    assert result["total_time"] == 0.0
    assert result["total_trades"] == 0


@pytest.mark.asyncio
async def test_time_execution_single_request():
    @time_execution
    async def single_request():
        return {"request_count": 1, "total_time": 100.0, "total_trades": 1}

    result = await single_request()
    assert result["request_count"] == 1
    assert result["total_time"] == 100.0
    assert result["total_trades"] == 1
