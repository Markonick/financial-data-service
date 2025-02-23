import asyncio
import random
import time

from typing import Optional

import httpx

from src.utils import time_execution  # Import the timing decorator

# List of real stock market symbols (same as in test_hft_stream.py)
REAL_SYMBOLS = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "FB",
    "BRK.A",
    "V",
    "JNJ",
    "WMT",
    # "JPM",
    # "NVDA",
    # "DIS",
    # "PYPL",
    # "MA",
    # "NFLX",
    # "ADBE",
    # "INTC",
    # "CMCSA",
    # "PFE",
]


@time_execution
async def simulate_stats_requests(num_requests: Optional[int] = None):
    request_count = 0
    total_time = 0.0

    async with httpx.AsyncClient() as client:
        while True:
            # Randomly select a symbol and k value
            symbol = random.choice(REAL_SYMBOLS)
            k = random.randint(1, 8)

            try:
                start_time = time.perf_counter()
                response = await client.get(f"http://localhost:8000/stats/{symbol}/{k}")
                response.raise_for_status()
                end_time = time.perf_counter()

                request_time = (end_time - start_time) * 1_000_000  # Convert to microseconds
                total_time += request_time
                request_count += 1

                if response.content:
                    print(f"\nStats for {symbol} (k={k}):")
                    print(response.json())
                else:
                    print("Empty response")

            except httpx.HTTPStatusError as e:
                print(
                    f"HTTP Error for {symbol} (k={k}): {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                print(f"Error querying stats for {symbol} (k={k}): {e!s}")

            await asyncio.sleep(random.uniform(0.01, 0.02))

            if num_requests is not None:
                num_requests -= 1
                if num_requests == 0:
                    break

    return {"request_count": request_count, "total_time": total_time, "total_trades": request_count}


async def main():
    num_requests = 1000  # Set to None for infinite requests
    await simulate_stats_requests(num_requests)


if __name__ == "__main__":
    asyncio.run(main())
