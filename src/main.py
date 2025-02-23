import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.constants import MAX_K, MIN_K
from src.exceptions import FinancialServiceError, InvalidWindowSizeError
from src.models import BatchData, BatchResponse, Stats
from src.services import SymbolManager

app = FastAPI(title="Financial Data Service")
symbol_manager = SymbolManager()


@app.exception_handler(FinancialServiceError)
async def financial_service_exception_handler(request, exc: FinancialServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.post("/add_batch/", response_model=BatchResponse, status_code=201)
async def add_batch(data: BatchData) -> BatchResponse:
    try:
        await symbol_manager.add_batch(data.symbol, data.values)
        return BatchResponse(status="success", message=f"Added batch for symbol: {data.symbol}")
    except Exception as e:
        logging.error(f"Error in add_batch: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/stats/{symbol}/{k}", response_model=Stats)
async def get_stats(symbol: str, k: int) -> Stats:
    if not MIN_K <= k <= MAX_K:
        raise InvalidWindowSizeError(k)
    return await symbol_manager.get_stats(symbol, k)


@app.get("/window_size/{symbol}/{k}")
async def get_window_size(symbol: str, k: int) -> dict:
    if not MIN_K <= k <= MAX_K:
        raise InvalidWindowSizeError(k)
    size = await symbol_manager.get_window_size(symbol, k)
    return {"size": size}
