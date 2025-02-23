import time
import asyncio
from functools import wraps
import sys
from loguru import logger

# Remove default handler and add our custom handler
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="{message}",  # Simplified format to let us handle the coloring
    level="INFO",
    colorize=True,
    enqueue=True,  # Ensure thread-safe logging
)


def time_execution(func):
    """
    Decorator to measure the execution time of an asynchronous function and log the number of requests,
    average time per request, and average time per trade.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1_000_000  # Convert to microseconds

        # Extract request count, total time, and batch size from the result if available
        request_count = result.get("request_count", 0)
        total_time = result.get("total_time", 0.0)
        total_trades = result.get("total_trades", 0)

        # Debug print
        logger.debug(f"total_trades: {total_trades}, request_count: {request_count}")

        average_time_per_request = total_time / request_count if request_count > 0 else None
        average_time_per_trade = total_time / total_trades if total_trades > 0 else None
        average_batch_size = total_trades / request_count if request_count > 0 else None

        # Format the numeric values with proper handling of None
        def format_value(value):
            if value is None:
                return "None"
            return f"{value:.2f}"

        # Get timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Create the log lines
        log_lines = [
            f"\033[32m{timestamp}\033[0m",  # Green timestamp
            f"\033[34mfunction:\033[0m \033[36m{func.__name__}\033[0m",
            f"\033[34mexecution_time_microseconds:\033[0m \033[33m{format_value(execution_time)}\033[0m",
            f"\033[34mtotal_requests:\033[0m \033[33m{request_count}\033[0m",
            f"\033[34mtotal_trades:\033[0m \033[33m{total_trades}\033[0m",  # Added for debugging
            f"\033[34maverage_batch_size:\033[0m \033[33m{format_value(average_batch_size)}\033[0m",
            f"\033[34maverage_time_per_request_microseconds:\033[0m \033[33m{format_value(average_time_per_request)}\033[0m",
            f"\033[34maverage_time_per_trade_microseconds:\033[0m \033[33m{format_value(average_time_per_trade)}\033[0m",
        ]

        # Find the longest line length (accounting for ANSI escape codes)
        max_length = max(
            len(
                line.replace("\033[32m", "")
                .replace("\033[34m", "")
                .replace("\033[36m", "")
                .replace("\033[33m", "")
                .replace("\033[37m", "")
                .replace("\033[0m", "")
            )
            for line in log_lines
        )

        # Create the box
        box_top = f"╔{'═' * (max_length + 2)}╗"
        box_bottom = f"╚{'═' * (max_length + 2)}╝"

        # Format the log data with the box
        formatted_log = "\n".join(
            [
                box_top,
                *[
                    f"║ {line}{' ' * (max_length - len(line.replace('\033[32m', '').replace('\033[34m', '').replace('\033[36m', '').replace('\033[33m', '').replace('\033[37m', '').replace('\033[0m', '')))} ║"
                    for line in log_lines
                ],
                box_bottom,
            ]
        )

        logger.info(formatted_log)

        return result

    return wrapper
