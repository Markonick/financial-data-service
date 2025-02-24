import asyncio
import logging

from collections import deque
from typing import Dict, List, Optional

import numpy as np

from .constants import MAX_K, MAX_SYMBOLS, MIN_K, WINDOW_SIZES
from .exceptions import MaxSymbolsReachedError, SymbolNotFoundError
from .models import Stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RunningStats:
    """
    Maintains running statistics for a fixed-size window of values, per symbol (x10).
    Uses a deque for O(1) operations and pre-calculated stats.
    """

    def __init__(self, window_size: int):
        """
        Initialize RunningStats with a fixed window size.
        """
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        self.current_min = np.float32(float("inf"))
        self.current_max = np.float32(float("-inf"))
        self.sum = np.float32(0.0)
        self.avg = np.float32(0.0)
        self.M2 = np.float32(0.0)

    def add(self, value: float) -> None:
        """Add a value to the running stats."""
        value = np.float32(value)

        if len(self.values) == self.window_size:
            old = self.values.popleft()
            self.sum = self.sum - old

            # Update for sliding window
            n = self.window_size
            old_avg = self.avg
            self.avg = self.avg + (value - old) / n

            # Update M2 by removing old value's contribution and adding new value's
            self.M2 = (
                self.M2
                - (old - old_avg) * (old - self.avg)
                + (value - old_avg) * (value - self.avg)
            )

            # Update min and max if we just removed a value that was min or max
            if old == self.current_min or old == self.current_max:
                self.current_min = min(self.values)
                self.current_max = max(self.values)
        else:
            # Welford's update for growing window
            n = len(self.values)
            delta = value - self.avg
            self.avg = self.avg + delta / (n + 1)
            self.M2 = self.M2 + delta * (value - self.avg)

        self.current_min = min(self.current_min, value)
        self.current_max = max(self.current_max, value)
        self.sum = self.sum + value
        self.values.append(value)

    def get_stats(self) -> Optional[Stats]:
        """
        Calculate statistics in O(1) time using running sums.
        """
        if not self.values:
            logger.warning("Attempted to get stats with no values")
            return None

        n = len(self.values)
        var = np.float32(self.M2) / np.float32(n) if n > 0 else np.float32(0)

        return Stats(
            min=float(self.current_min),
            max=float(self.current_max),
            last=float(self.values[-1]),
            avg=float(self.avg),
            var=float(var),
            values=n,
        )


class SymbolManager:
    """
    Manages multiple symbols' trading data with efficient statistical calculations.
    Provides O(1) stats retrieval and O(b) batch updates.
    """

    def __init__(self):
        self.symbols: Dict[str, Dict[int, RunningStats]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def add_batch(self, symbol: str, values: List[float]) -> None:
        """
        Add a batch of values for a symbol.

        Time Complexity: O(b * k) where:
        - b is len(values) (max 10000)
        - k is number of window sizes (constant: 8)

        Space Complexity: O(k * w) for new symbols

        Raises ValueError if attempting to add more than MAX_SYMBOLS unique symbols
        """
        if symbol not in self.locks:
            self.locks[symbol] = asyncio.Lock()

        async with self.locks[symbol]:
            if symbol not in self.symbols:
                if len(self.symbols) >= MAX_SYMBOLS:
                    logger.error(f"Failed to add symbol {symbol}: MAX_SYMBOLS limit reached")
                    raise MaxSymbolsReachedError(MAX_SYMBOLS)

                # Initialize RunningStats for each window size
                self.symbols[symbol] = {
                    k: RunningStats(window_size=WINDOW_SIZES[k]) for k in range(MIN_K, MAX_K + 1)
                }

            # Update all window sizes with new values
            for value in values:
                for stats in self.symbols[symbol].values():
                    stats.add(value)

    async def get_stats(self, symbol: str, k: int) -> Stats:
        """
        Get statistics for a symbol's last 10^k values

        Time Complexity: O(1) - constant time retrieval
        Space Complexity: O(1) - returns fixed-size Stats object

        Raises:
            SymbolNotFoundError: if symbol doesn't exist
        """
        if symbol not in self.locks:
            self.locks[symbol] = asyncio.Lock()

        async with self.locks[symbol]:
            if symbol not in self.symbols:
                logger.error(f"Stats request failed: Symbol {symbol} not found")
                raise SymbolNotFoundError(symbol)

            stats = self.symbols[symbol][k].get_stats()
            if stats is None:
                logger.error(f"Stats request failed: No data for symbol {symbol}")
                raise SymbolNotFoundError(symbol)

            logger.debug(f"Retrieved stats for {symbol} with k={k}")
            return stats
