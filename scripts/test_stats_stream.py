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
    "JPM",
    "NVDA",
    "DIS",
    "PYPL",
    "MA",
    "NFLX",
    "ADBE",
    "INTC",
    "CMCSA",
    "PFE",
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

            # Random delay between requests (0.1 to 0.2 second) per batch = ms per data-point
            await asyncio.sleep(random.uniform(0.1, 0.2))

            if num_requests is not None:
                num_requests -= 1
                if num_requests == 0:
                    break


async def main():
    num_requests = 15  # Adjust this number as needed
    print(f"Starting {num_requests} random stats requests...")
    await simulate_stats_requests(num_requests)
    print("\nFinished stats requests simulation")


if __name__ == "__main__":
    asyncio.run(main())
