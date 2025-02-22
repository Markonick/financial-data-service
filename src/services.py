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
        self.window_size = window_size
        self.values: deque[np.float32] = deque(maxlen=window_size)

        # Running stats
        self.sum: np.float32 = np.float32(0.0)
        self.sum_squared: np.float32 = np.float32(0.0)
        self.current_min: np.float32 = np.float32(np.inf)
        self.current_max: np.float32 = np.float32(-np.inf)

    def add(self, value: float) -> None:
        """Add a new value and update running statistics"""

        # Store value as float32 to save memory
        value16 = np.float32(value)
        value32 = np.float32(value)  # Use float32 for calculations

        # If window is full, remove oldest value's contribution
        if len(self.values) == self.window_size:
            oldest = self.values.popleft()
            oldest32 = np.float32(oldest)
            self.sum -= oldest32
            self.sum_squared -= oldest32 * oldest32

            # If oldest was min/max, recalculate from window
            if oldest == self.current_min or oldest == self.current_max:
                self.current_min = np.float32(min(self.values))
                self.current_max = np.float32(max(self.values))

        # Add new value
        self.values.append(value16)
        self.sum += value32
        self.sum_squared += value32 * value32

        # Update min/max
        if value16 < self.current_min:
            self.current_min = value16
        if value16 > self.current_max:
            self.current_max = value16

    def get_stats(self) -> Optional[Stats]:
        """Calculate statistics in O(1) time using running sums"""
        if not self.values:
            return None

        n = len(self.values)
        avg = self.sum / n
        var = (self.sum_squared / n) - (avg * avg)

        return Stats(
            min=float(self.current_min),
            max=float(self.current_max),
            last=float(self.values[-1]),
            avg=float(avg),
            var=float(var),
            curr_window_size=n,
        )


class SymbolManager:
    """Manages trading data for multiple symbols"""

    def __init__(self):
        self.symbols: Dict[str, Dict[int, RunningStats]] = {}

    def add_batch(self, symbol: str, values: List[float]) -> None:
        """
        Add a batch of values for a symbol.

        Time Complexity: O(b * k) where:
        - b is len(values) (max 10000)
        - k is number of window sizes (constant: 8)

        Space Complexity: O(k * w) for new symbols

        Raises ValueError if attempting to add more than MAX_SYMBOLS unique symbols
        """
        if symbol not in self.symbols:
            if len(self.symbols) >= MAX_SYMBOLS:
                raise MaxSymbolsReachedError(MAX_SYMBOLS)
            # Initialize RunningStats for each window size
            self.symbols[symbol] = {
                k: RunningStats(window_size=WINDOW_SIZES[k]) for k in range(MIN_K, MAX_K + 1)
            }

        # Update all window sizes with new values
        for value in values:
            for stats in self.symbols[symbol].values():
                stats.add(value)

    def get_stats(self, symbol: str, k: int) -> Stats:
        """
        Get statistics for a symbol's last 10^k values

        Time Complexity: O(1) - constant time retrieval
        Space Complexity: O(1) - returns fixed-size Stats object

        Raises:
            SymbolNotFoundError: if symbol doesn't exist
        """
        if symbol not in self.symbols or k not in self.symbols[symbol]:
            raise SymbolNotFoundError(symbol)

        stats = self.symbols[symbol][k].get_stats()
        if stats is None:
            raise SymbolNotFoundError(symbol)

        return stats
