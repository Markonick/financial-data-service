from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .constants import MAX_K, MIN_K
from .exceptions import FinancialServiceError, InvalidWindowSizeError
from .models import BatchData, BatchResponse, Stats
from .services import SymbolManager

app = FastAPI(title="Financial Data Service")
symbol_manager = SymbolManager()


@app.exception_handler(FinancialServiceError)
async def financial_service_exception_handler(request, exc: FinancialServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.post("/add_batch/", response_model=BatchResponse, status_code=201)
async def add_batch(data: BatchData) -> BatchResponse:
    symbol_manager.add_batch(data.symbol, data.values)
    return BatchResponse(status="success", message=f"Added batch for symbol: {data.symbol}")


@app.get("/stats/{symbol}/{k}", response_model=Stats)
async def get_stats(symbol: str, k: int) -> Stats:
    if not MIN_K <= k <= MAX_K:
        raise InvalidWindowSizeError(k)
    return symbol_manager.get_stats(symbol, k)
