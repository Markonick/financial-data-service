import pytest

from pydantic import ValidationError

from src.constants import MAX_BATCH_SIZE
from src.models import BatchData, Stats


def test_batch_data_valid():
    batch = BatchData(symbol="AAPL", values=[1.0, 2.0, 3.0])
    assert batch.symbol == "AAPL"
    assert batch.values == [1.0, 2.0, 3.0]


def test_batch_data_empty_values():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values=[])
    assert "Values cannot be empty" in str(exc_info.value)


def test_batch_data_single_value():
    batch = BatchData(symbol="AAPL", values=[1.0])
    assert batch.values == [1.0]


def test_batch_data_max_values():
    # Test with exactly MAX_BATCH_SIZE values
    values = [1.0] * MAX_BATCH_SIZE
    batch = BatchData(symbol="AAPL", values=values)
    assert len(batch.values) == MAX_BATCH_SIZE


def test_batch_data_exceeds_max_values():
    # Test with MAX_BATCH_SIZE + 1 values
    values = [1.0] * (MAX_BATCH_SIZE + 1)
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values=values)
    assert f"Batch size cannot exceed {MAX_BATCH_SIZE} values" in str(exc_info.value)


def test_stats_creation():
    stats = Stats(min=1.0, max=2.0, avg=1.5, var=1.5654, last=2.0, values=5)
    assert stats.min == 1.0
    assert stats.max == 2.0
    assert stats.avg == 1.5
    assert stats.var == 1.5654
    assert stats.last == 2.0
    assert stats.values == 5


def test_batch_data_invalid_symbol_type():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol=123, values=[1.0])
    assert "Input should be a valid string" in str(exc_info.value)


def test_batch_data_invalid_values_type():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values="not a list")
    assert "Input should be a valid list" in str(exc_info.value)


def test_batch_data_invalid_value_types_in_list():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values=[1.0, "abc", 3.0])  # "abc" can't be converted to float
    error_msg = str(exc_info.value)
    assert "Input should be a valid number" in error_msg


def test_batch_data_mixed_value_types_in_list():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values=[1.0, None, 3.0])  # None can't be converted to float
    error_msg = str(exc_info.value)
    assert "Input should be a valid number" in error_msg


def test_batch_data_non_numeric_values():
    with pytest.raises(ValidationError) as exc_info:
        BatchData(symbol="AAPL", values=["abc", "def", "ghi"])
    error_msg = str(exc_info.value)
    assert "Input should be a valid number" in error_msg


def test_batch_data_missing_fields():
    # Test missing symbol
    with pytest.raises(ValidationError):
        BatchData(values=[1.0])

    # Test missing values
    with pytest.raises(ValidationError):
        BatchData(symbol="AAPL")
