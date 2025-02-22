from typing import List

from pydantic import BaseModel, field_validator

from .constants import MAX_BATCH_SIZE


class Stats(BaseModel):
    min: float
    max: float
    last: float
    avg: float
    var: float
    curr_window_size: int


class BatchResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    detail: str


class BatchData(BaseModel):
    symbol: str
    values: List[float]

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, symbol: str) -> str:
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        return symbol

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: List[float]) -> List[float]:
        if not isinstance(values, list):
            raise ValueError("Values must be a list")
        if not values:
            raise ValueError("Values cannot be empty")
        if len(values) > MAX_BATCH_SIZE:
            raise ValueError(f"Batch size cannot exceed {MAX_BATCH_SIZE} values")
        if not all(isinstance(value, (int, float)) for value in values):
            raise ValueError("All values must be numbers")
        return values
