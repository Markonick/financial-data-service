# Batch limits
MAX_BATCH_SIZE = 10000
MAX_SYMBOLS = 10

# Window size limits
MIN_K = 1
MAX_K = 8

# Window sizes for stats (10^k where k is 1-8)
WINDOW_SIZES = {k: 10**k for k in range(MIN_K, MAX_K + 1)}
