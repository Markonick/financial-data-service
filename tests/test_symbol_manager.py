import pytest

from src.constants import MAX_SYMBOLS, MIN_K
from src.exceptions import MaxSymbolsReachedError, SymbolNotFoundError
from src.services import SymbolManager


def test_symbol_manager_initialization():
    manager = SymbolManager()
    assert len(manager.symbols) == 0


@pytest.mark.asyncio
async def test_symbol_manager_max_symbols():
    manager = SymbolManager()
    # Add MAX_SYMBOLS symbols
    for i in range(MAX_SYMBOLS):
        await manager.add_batch(f"SYMBOL{i}", [1.0])

    # Try to add one more
    with pytest.raises(MaxSymbolsReachedError):
        await manager.add_batch("EXTRA", [1.0])


@pytest.mark.asyncio
async def test_symbol_manager_window_sizes():
    manager = SymbolManager()
    await manager.add_batch("AAPL", [1.0, 2.0, 3.0])
    stats = await manager.get_stats("AAPL", 1)
    assert stats is not None


@pytest.mark.asyncio
async def test_symbol_manager_get_stats_nonexistent_symbol():
    manager = SymbolManager()
    with pytest.raises(SymbolNotFoundError):
        await manager.get_stats("NONEXISTENT", 1)


@pytest.mark.asyncio
async def test_symbol_manager_batch_processing():
    manager = SymbolManager()

    # Add batch of values
    values = [1.0, 2.0, 3.0]
    await manager.add_batch("AAPL", values)

    # Check stats for different window sizes
    stats_k1 = await manager.get_stats("AAPL", 1)  # window_size = 10
    assert stats_k1.min == 1.0
    assert stats_k1.max == 3.0
