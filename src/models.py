from math import isfinite
from typing import List

from pydantic import BaseModel, field_validator

from .constants import MAX_BATCH_SIZE


class Stats(BaseModel):
    min: float
    max: float
    last: float
    avg: float
    var: float
    values: int


class BatchResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    detail: str


class BatchData(BaseModel):
    """
    Model for batch data input validation.

    Attributes:
        symbol (str): Stock market symbol identifier
        values (List[float]): List of trading values
    """

    symbol: str
    values: List[float]

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, symbol: str) -> str:
        """
        Validate symbol is not empty.
        """
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        return symbol

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: List[float]) -> List[float]:
        """
        Validate list of trading values.
        """
        if not isinstance(values, list):
            raise ValueError("Values must be a list")
        if not values:
            raise ValueError("Values cannot be empty")
        if len(values) > MAX_BATCH_SIZE:
            raise ValueError(f"Batch size cannot exceed {MAX_BATCH_SIZE} values")
        if not all(isinstance(value, (int, float)) for value in values):
            raise ValueError("All values must be numbers")
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("All values must be finite numbers")
        return values
