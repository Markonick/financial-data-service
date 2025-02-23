import pytest

from src.constants import MAX_SYMBOLS
from src.exceptions import MaxSymbolsReachedError, SymbolNotFoundError
from src.services import SymbolManager


def test_symbol_manager_initialization():
    manager = SymbolManager()
    assert len(manager.symbols) == 0


def test_symbol_manager_max_symbols():
    manager = SymbolManager()
    values = [1.0, 2.0, 3.0]

    # Add MAX_SYMBOLS different symbols
    for i in range(MAX_SYMBOLS):
        manager.add_batch(f"SYMBOL{i}", values)

    # Try to add one more symbol
    with pytest.raises(MaxSymbolsReachedError) as exc_info:
        manager.add_batch("TOOMANY", values)
    assert f"Maximum number of symbols ({MAX_SYMBOLS}) reached" in str(exc_info.value)


def test_symbol_manager_window_sizes():
    manager = SymbolManager()
    manager.add_batch("AAPL", [1.0])

    # Check all window sizes were created
    assert len(manager.symbols["AAPL"]) == 8
    for k in range(1, 9):
        assert k in manager.symbols["AAPL"]
        assert manager.symbols["AAPL"][k].window_size == 10**k


def test_symbol_manager_get_stats_nonexistent_symbol():
    manager = SymbolManager()

    with pytest.raises(SymbolNotFoundError) as exc_info:
        manager.get_stats("NOSUCH", 1)
    assert str(exc_info.value) == "Symbol NOSUCH not found"


def test_symbol_manager_batch_processing():
    manager = SymbolManager()

    # Add batch of values
    values = [1.0, 2.0, 3.0]
    manager.add_batch("AAPL", values)

    # Check stats for different window sizes
    stats_k1 = manager.get_stats("AAPL", 1)  # window_size = 10
    assert stats_k1.min == 1.0
    assert stats_k1.max == 3.0
