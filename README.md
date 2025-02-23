<h1 align="center">Welcome to financial-data-service 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />
</p>

> 📈 High-Performance Financial Data Service
⚡️ Real-time Stats | 📊 O(1) Retrieval | 🔄 Streaming Data

## Prerequisites

Before running the project, ensure you have the following installed on your system:

### Required
- Python 3.13 (`python3 --version`)
- Poetry (`poetry --version`)
- Make (`make --version`)
  *** Optional:
- tmux
- htop
  
### System Libraries (Ubuntu/Debian)
## Install

```sh
make install
```

## Usage

```sh
make run
```
This will start the FastAPI app running off an asgi uvicorn server.
However, we need to interact with it. In that respect, you can find some scripts in the scripts
folder. 
- The first one mocks asynchronous stream of high-frequency **/add_batch** POST requests.
- The second one will start randomly sending GET requests to the **/stats** endpoint

You can also use command
```sh
make start-all
```

which will start a tmux session (as long as you have already installed it, check Prerequisites).
in a quadrant setup.
- Top-left: FastAPI server **(make stats)**
- Top-right: Get stats **(make stats)**
- Bottom-left: Post batches **(make batches)**
- Bottom-right: Htop monitor **(make monitor)**

![Tmux](images/tmux.gif)

Run this script to give your mouse control of tmux:
```sh
tmux source-file .tmux.conf
```
## Testing

### Current Test Coverage
The test suite covers:
1. Unit Tests (`tests/`)
   - `test_running_stats.py`: Tests statistical calculations
   - `test_symbol_manager.py`: Tests symbol management operations
   - `test_exceptions.py`: Tests error handling
   - `test_endpoints.py`: Tests API endpoints

2. Load Testing Scripts (`scripts/`)
   - `test_hft_stream.py`: Simulates high-frequency trading data ingestion
   - `test_stats_stream.py`: Simulates concurrent stats retrieval

### Run All Tests
```sh
make test
```
### Run Tests with Coverage
```sh
make test-cov
```
### Run Specific Test Method
```sh
make test-method file=test_running_stats.py method=test_running_stats_initialization
```
### Run Specific Test File
```sh
make test-file file=test_running_stats.py
```

```

Compact version:
┌─────────┐    ┌─────────┐    ┌─────────────┐
│ Client  │───▶│ FastAPI │───▶│SymbolManager│
└─────────┘    └─────────┘    └─────┬───────┘
                                    │
                              ┌─────┴──────┐
                              │RunningStats│
                              └────────────┘
```

```

More detail:

┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Client     │────▶│  FastAPI Server │────▶│SymbolManager │
└──────────────┘     └─────────────────┘     └──────────────┘
                            │                        │
                            │                  ┌─────┴────────┐
                            │                  │              │
                     ┌──────┴──────┐     ┌─────┴──────┐  ┌────┴────┐
                     │Input Models │     │RunningStats│  │  Deque  │
                     │(Validation) │     │(k=1...8)   │  │Windows  │
                     └─────────────┘     └────────────┘  └─────────┘

Data Flow:
POST /add_batch/ ──▶ BatchData ──▶ SymbolManager ──▶ RunningStats[k] ──▶ Deque
GET /stats/{k}   ◀── Stats    ◀── O(1) lookup  ◀── Pre-calculated
```

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
   - Python's deque provides O(1) append and pop from left side without shifting N samples
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

## Performance Characteristics

### Memory Usage (float32 values)
Per Symbol Memory:
- k=1: 10¹ values = 40 bytes
- k=2: 10² values = 400 bytes
- k=3: 10³ values = 4 KB
- k=4: 10⁴ values = 40 KB
- k=5: 10⁵ values = 400 KB
- k=6: 10⁶ values = 4 MB
- k=7: 10⁷ values = 40 MB
- k=8: 10⁸ values = 400 MB
Total per symbol: ~444.45 MB
Maximum (10 symbols): ~4.5 GB

### Throughput
- Batch Processing: ~50,000 points/second
  - 10,000 points every 200ms
  - Each point = 0.02ms


## API Endpoints
- `POST /add_batch/`: Add a batch of trading data.
- `GET /stats/`: Retrieve statistics for a symbol.

### Access the API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

![Swagger](images/swagger.png)
![Redoc](images/redoc.png)

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
## Author

👤 **Nicolas Markos**

* Github: [@markonick](https://github.com/markonick)
* LinkedIn: [@Nicolas Markos](https://www.linkedin.com/in/nicolas-markos-54865211/)

## Show your support

Give a ⭐️ if this project helped you!

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_