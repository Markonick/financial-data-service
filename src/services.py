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
        self.values: deque[np.float32] = deque(maxlen=window_size)

        # Running stats
        self.sum: np.float32 = np.float32(0.0)
        self.sum_squared: np.float32 = np.float32(0.0)
        self.current_min: np.float32 = np.float32(np.inf)
        self.current_max: np.float32 = np.float32(-np.inf)
        logger.debug(f"Initialized RunningStats with window_size={window_size}")

    def add(self, value: float) -> None:
        """
        Add a new value and update running statistics.
        """
        value32 = np.float32(value)
        if len(self.values) == self.window_size:
            oldest = self.values.popleft()
            oldest32 = np.float32(oldest)
            self.sum -= oldest32
            self.sum_squared -= oldest32 * oldest32
            logger.debug(f"Window full, removing oldest value: {oldest}")

            # If oldest was min/max, recalculate from window
            if oldest == self.current_min or oldest == self.current_max:
                self.current_min = np.float32(min(self.values))
                self.current_max = np.float32(max(self.values))

        # Add new value
        self.values.append(value32)
        self.sum += value32
        self.sum_squared += value32 * value32

        # Update min/max
        if value32 < self.current_min:
            logger.debug(f"New minimum value: {value32}")
            self.current_min = value32
        if value32 > self.current_max:
            logger.debug(f"New maximum value: {value32}")
            self.current_max = value32

    def get_stats(self) -> Optional[Stats]:
        """
        Calculate statistics in O(1) time using running sums.
        """
        if not self.values:
            logger.warning("Attempted to get stats with no values")
            return None

        n = len(self.values)
        avg = self.sum / n

        # More numerically stable variance calculation
        squared_diff_sum = sum((x - avg) ** 2 for x in self.values)
        var = squared_diff_sum / n

        return Stats(
            min=float(self.current_min),
            max=float(self.current_max),
            last=float(self.values[-1]),
            avg=float(avg),
            var=float(var),
            values=len(self.values),
        )


class SymbolManager:
    """
    Manages multiple symbols' trading data with efficient statistical calculations.
    Provides O(1) stats retrieval and O(b) batch updates.
    """

    def __init__(self):
        self.symbols: Dict[str, Dict[int, RunningStats]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        logger.debug("Initialized SymbolManager")

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
                logger.debug(f"Adding new symbol: {symbol}")
                # Initialize RunningStats for each window size
                self.symbols[symbol] = {
                    k: RunningStats(window_size=WINDOW_SIZES[k]) for k in range(MIN_K, MAX_K + 1)
                }

            logger.debug(f"Adding batch of {len(values)} values for {symbol}")
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
