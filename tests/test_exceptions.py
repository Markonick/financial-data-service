from src.exceptions import FinancialServiceError, MaxSymbolsReachedError, SymbolNotFoundError


def test_financial_service_error():
    error = FinancialServiceError("Test error", status_code=400)
    assert str(error) == "Test error"
    assert error.status_code == 400


def test_max_symbols_reached_error():
    max_symbols = 10
    error = MaxSymbolsReachedError(max_symbols)
    assert str(error) == f"Maximum number of symbols ({max_symbols}) reached"
    assert error.status_code == 400


def test_symbol_not_found_error():
    symbol = "AAPL"
    error = SymbolNotFoundError(symbol)
    assert str(error) == f"Symbol {symbol} not found"
    assert error.status_code == 404


def test_error_inheritance():
    # Test that our custom errors inherit correctly
    error1 = MaxSymbolsReachedError(10)
    error2 = SymbolNotFoundError("AAPL")

    assert isinstance(error1, FinancialServiceError)
    assert isinstance(error2, FinancialServiceError)
