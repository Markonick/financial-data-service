import asyncio
import random

from pprint import pprint
from typing import Optional

import httpx
import numpy as np

from src.models import BatchData

# List of real stock market symbols
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


async def simulate_hft_stream(batch_size: int, batch_count: Optional[int] = None):
    async with httpx.AsyncClient() as client:
        while True:
            symbol = random.choice(REAL_SYMBOLS)

            # Generate random float32 values between 0 and 10000 and format to 2 decimal places
            values = np.random.uniform(0, 10000, batch_size).astype(np.float32)
            values = [round(float(value), 2) for value in values]

            batch_data = BatchData(symbol=symbol, values=values)

            try:
                response = await client.post(
                    "http://localhost:8000/add_batch/",
                    json=batch_data.model_dump(),  # Using model_dump instead of dict
                )
                response.raise_for_status()  # Raise exception for bad status codes

                if response.content:  # Check if there's content before parsing JSON
                    print(f"Response for {symbol}:")
                    pprint(response.json())
                else:
                    print(f"Empty response for {symbol}")

            except httpx.HTTPStatusError as e:
                print(f"Error processing {symbol}: {e}")
                print(f"Response content: {e.response.text}")
            except Exception as e:
                print(f"Unexpected error processing {symbol}: {str(e)}")

            # 10,000 points every 200ms = ~50,000 points/second
            # Each point = 0.02ms
            # await asyncio.sleep(0.2)  # 200ms between batches
            # await asyncio.sleep(2)  # 200ms between batches

            if batch_count is not None:
                batch_count -= 1
                if batch_count == 0:
                    break


async def main():
    await simulate_hft_stream(10000, 10)


if __name__ == "__main__":
    asyncio.run(main())
