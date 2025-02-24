import asyncio
import logging
import random
import time

from typing import List, Optional

import httpx
import numpy as np

from src.models import BatchData
from src.utils import time_execution  # Import the timing decorator

# Constants
REAL_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "FB", "BRK.A", "V", "JNJ", "WMT"]
BATCH_DELAY = 1e-6  # 1 microsecond delay between batches
MAX_VALUE = 10000  # Maximum value for random generation
MIN_VALUE = 0  # Minimum value for random generation
MIN_BATCH_SIZE = 1  # Minimum batch size
MAX_BATCH_SIZE = 10000  # Maximum batch size

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure connection pool
transport = httpx.AsyncHTTPTransport(
    limits=httpx.Limits(max_keepalive_connections=100, max_connections=100, keepalive_expiry=5.0)
)

# Create a single client for reuse
client = httpx.AsyncClient(transport=transport, timeout=30.0, base_url="http://localhost:8000")


def generate_random_values(size: int) -> List[float]:
    return list(np.random.uniform(MIN_VALUE, MAX_VALUE, size))


@time_execution
async def simulate_hft_stream(batch_count: Optional[int] = None):
    """
    Simulate a high-frequency trading data stream by sending batches of random values
    to a RESTful service endpoint.

    Args:
        batch_count (Optional[int]): Number of batches to send. If None, run indefinitely.

    Returns:
        dict: Contains request_count, total_time, and total_trades for logging purposes.
    """
    request_count = 0
    total_time = 0.0
    total_trades = 0

    try:
        while True:
            symbol = random.choice(REAL_SYMBOLS)
            batch_size = random.randint(MIN_BATCH_SIZE, MAX_BATCH_SIZE)
            values = generate_random_values(batch_size)
            batch_data = BatchData(symbol=symbol, values=values)

            try:
                start_time = time.perf_counter()
                response = await client.post("/add_batch/", json=batch_data.model_dump())
                response.raise_for_status()
                end_time = time.perf_counter()

                request_time = (end_time - start_time) * 1_000_000  # Convert to microseconds
                total_time += request_time
                request_count += 1
                total_trades += len(values)

                if response.content:
                    logger.info("Response for %s: %s", symbol, response.json())
                else:
                    logger.info("Empty response for %s", symbol)

            except Exception as e:
                logger.error(f"Error sending batch: {e!s}")

            if batch_count is not None:
                if request_count >= batch_count:
                    break

            await asyncio.sleep(BATCH_DELAY)

    finally:
        # Ensure we close the client properly
        await client.aclose()

    return {"request_count": request_count, "total_time": total_time, "total_trades": total_trades}


# Example usage
if __name__ == "__main__":
    asyncio.run(simulate_hft_stream(batch_count=1000))
