import numpy as np
import pytest

from src.services import RunningStats


@pytest.fixture
def stock_window():
    return [142.35, 144.50, 143.75, 145.20, 141.90]  # Day 1  # Day 2  # Day 3  # Day 4  # Day 5


def test_running_stats_initialization():
    stats = RunningStats(window_size=3)
    assert stats.window_size == 3
    assert len(stats.values) == 0
    assert stats.sum == 0.0
    assert stats.sum_squared == 0.0
    assert stats.current_min == np.float16(np.inf)
    assert stats.current_max == np.float16(-np.inf)


def test_running_stats_basic_flow():
    stats = RunningStats(window_size=3)

    # Add first value
    stats.add(1.0)
    assert len(stats.values) == 1
    assert stats.current_min == 1.0
    assert stats.current_max == 1.0
    assert stats.sum == 1.0

    # Add second value
    stats.add(2.0)
    assert len(stats.values) == 2
    assert stats.current_min == 1.0
    assert stats.current_max == 2.0
    assert stats.sum == 3.0


def test_running_stats_window_full():
    stats = RunningStats(window_size=3)

    # Fill window
    stats.add(1.0)  # [1]
    stats.add(2.0)  # [1, 2]
    stats.add(3.0)  # [1, 2, 3]
    assert len(stats.values) == 3
    assert stats.current_min == 1.0
    assert stats.current_max == 3.0

    # Add value when window is full
    stats.add(4.0)  # [2, 3, 4] (1.0 leaves)
    assert len(stats.values) == 3
    assert list(stats.values) == [2.0, 3.0, 4.0]
    assert stats.current_min == 2.0
    assert stats.current_max == 4.0


def test_running_stats_min_max_updates():
    stats = RunningStats(window_size=3)

    # Test min updates
    stats.add(3.0)  # [3]
    stats.add(1.0)  # [3, 1]
    stats.add(2.0)  # [3, 1, 2]
    assert stats.current_min == 1.0
    stats.add(0.5)  # [1, 2, 0.5] (3 leaves)
    assert stats.current_min == 0.5

    # Test max updates
    stats.add(5.0)  # [2, 0.5, 5] (1 leaves)
    assert stats.current_max == 5.0


def test_running_stats_get_stats():
    stats = RunningStats(window_size=3)

    # Empty stats
    assert stats.get_stats() is None

    # Single value
    stats.add(2.0)
    result = stats.get_stats()
    assert result.min == 2.0
    assert result.max == 2.0
    assert result.last == 2.0
    assert result.avg == 2.0
    assert result.var == 0.0


def test_running_stats_precision():
    stats = RunningStats(window_size=2)

    # Test float16 precision
    large_value = 65504.0  # max float16
    stats.add(large_value)
    stats.add(1.0)
    result = stats.get_stats()
    assert result.min == 1.0
    assert result.max == large_value


def test_mean_calculation(stock_window):
    stats = RunningStats(window_size=5)
    # Exact calculation:
    # (142.35 + 144.50 + 143.75 + 145.20 + 141.90) / 5 = 143.54
    expected_mean = 143.54

    for value in stock_window:
        stats.add(value)

    result = stats.get_stats()
    assert abs(result.avg - expected_mean) < 0.01
    assert result.avg == pytest.approx(143.54, abs=0.01)


def test_variance_calculation(stock_window):
    stats = RunningStats(window_size=5)
    # Variance calculation:
    # 1. Mean = 143.54
    # 2. Squared differences from mean:
    #    (142.35 - 143.54)² = 1.4161
    #    (144.50 - 143.54)² = 0.9216
    #    (143.75 - 143.54)² = 0.0441
    #    (145.20 - 143.54)² = 2.7556
    #    (141.90 - 143.54)² = 2.6896
    # 3. Sum = 7.827
    # 4. Divide by n = 7.827/5 = 1.5654
    expected_variance = 1.5654

    for value in stock_window:
        stats.add(value)

    result = stats.get_stats()
    assert abs(result.var - expected_variance) < 0.01
    assert result.var == pytest.approx(1.5654, abs=0.01)


def test_window_sliding(stock_window):
    stats = RunningStats(window_size=5)
    for value in stock_window:
        stats.add(value)

    new_value = 146.80  # Day 6
    stats.add(new_value)

    # New window: [144.50, 143.75, 145.20, 141.90, 146.80]
    # New mean: (144.50 + 143.75 + 145.20 + 141.90 + 146.80) / 5 = 144.43
    # New variance calculation:
    # 1. Mean = 144.43
    # 2. Squared differences:
    #    (144.50 - 144.43)² = 0.0049
    #    (143.75 - 144.43)² = 0.4624
    #    (145.20 - 144.43)² = 0.5929
    #    (141.90 - 144.43)² = 6.4009
    #    (146.80 - 144.43)² = 5.6169
    # 3. Sum = 13.078
    # 4. Divide by n = 13.078/5 = 2.6156

    result = stats.get_stats()
    assert result.avg == pytest.approx(144.43, abs=0.01)
    assert result.var == pytest.approx(2.6156, abs=0.01)
