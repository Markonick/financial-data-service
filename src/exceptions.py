from fastapi import HTTPException

from .constants import MAX_K, MIN_K


class FinancialServiceError(HTTPException):
    def __init__(self, message: str, status_code: int = 400):
        self.status_code = status_code
        self.message = message
        super().__init__(status_code=status_code, detail=message)

    def __str__(self) -> str:
        return self.message


class SymbolNotFoundError(FinancialServiceError):
    def __init__(self, symbol: str):
        super().__init__(f"Symbol {symbol} not found", status_code=404)


class MaxSymbolsReachedError(FinancialServiceError):
    def __init__(self, max_symbols: int):
        super().__init__(f"Maximum number of symbols ({max_symbols}) reached", status_code=400)


class InvalidWindowSizeError(FinancialServiceError):
    def __init__(self, k: int):
        super().__init__(
            f"Window size exponent (k={k}) must be between {MIN_K} and {MAX_K}", status_code=422
        )
