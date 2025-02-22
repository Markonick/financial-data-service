# Financial Data Service

A high-performance RESTful service for handling high-frequency trading data.

## Technical Documentation

### Architecture

#### SymbolManager
Main service class managing trading data for multiple symbols.

Time Complexity:
- add_batch: O(b * k) where:
  - b is the batch size (max 10000)
  - k is the number of window sizes (constant: 8)
  Therefore, effectively O(b) for each batch

- get_stats: O(1) - constant time retrieval of pre-calculated stats

Space Complexity:
- O(s * k * w) where:
  - s is number of symbols (max 10)
  - k is number of window sizes (constant: 8)
  - w is largest window size (10^8)
  Therefore, O(10 * 8 * 10^8) = O(8 * 10^9) in worst case

Design Decisions:
1. Pre-calculate statistics for all window sizes on insertion
   - Trades more space for constant-time stats retrieval
   - Suitable for read-heavy workloads

2. Use deque with maxlen for each window
   - Python's deque provides O(1) append and pop from both ends
   - Automatically maintains fixed size (drops old values when maxlen reached)
   - Thread-safe for individual operations

3. Separate RunningStats instance per window size
   - Allows parallel processing if needed
   - Simplifies stats calculation logic

#### RunningStats
Statistics calculator for a fixed-size window of values.

Time Complexity:
- add: O(1) - constant time insertion and stats update using deque
- get_stats: O(1) - constant time retrieval of pre-calculated stats

Space Complexity:
- O(w) where w is the window size (stores only the last w values in deque)

### System Constraints
- Maximum 10 unique symbols
- Batch size limit: 10000 values
- Window sizes: 10^k where k is 1-8
- In-memory storage only
- No concurrent requests for the same symbol

## Overview
This service provides a high-performance API for managing and analyzing financial trading data.

## Setup
1. Install dependencies: `poetry install`
2. Run the application: `make run`

## API Endpoints
- `POST /add_batch/`: Add a batch of trading data.
- `GET /stats/`: Retrieve statistics for a symbol.


## Project Structure
```
financial-data-service/
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── services.py      # Business logic (SymbolManager, RunningStats)
|   |...
├── tests/
│   ├── __init__.py
│   ├── test_main.py     # Tests for the FastAPI endpoints
│   ├── test_services.py # Tests for the business logic
|   |...
├── .gitignore
├── Makefile
├── poetry.lock
├── pyproject.toml
├── ...
└── README.md
```

