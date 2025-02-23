import asyncio
import random

from pprint import pprint
from typing import Optional

import httpx

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


async def simulate_stats_requests(num_requests: Optional[int] = None):
    async with httpx.AsyncClient() as client:
        while True:
            # Randomly select a symbol and k value
            symbol = random.choice(REAL_SYMBOLS)
            k = random.randint(1, 8)

            try:
                response = await client.get(f"http://localhost:8000/stats/{symbol}/{k}")
                response.raise_for_status()

                print(f"\nStats for {symbol} (k={k}):")
                if response.content:
                    pprint(response.json())
                else:
                    print("Empty response")

            except httpx.HTTPStatusError as e:
                print(
                    f"HTTP Error for {symbol} (k={k}): {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                print(f"Error querying stats for {symbol} (k={k}): {str(e)}")

            # Random delay between requests (0.01 to 0.02 second) per batch = 1-2 ms per request
            await asyncio.sleep(random.uniform(0.01, 0.02))

            if num_requests is not None:
                num_requests -= 1
                if num_requests == 0:
                    break


async def main():
    num_requests = None  # Adjust this number as needed

    await simulate_stats_requests()


if __name__ == "__main__":
    asyncio.run(main())
