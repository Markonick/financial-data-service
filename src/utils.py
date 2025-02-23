import sys
import time

from functools import wraps

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
    Decorator to measure the execution time of an asynchronous function and log
    the number of requests, average time per request, and average time per trade.
    """
    # ANSI color codes
    green = "\033[32m"
    blue = "\033[34m"
    cyan = "\033[36m"
    yellow = "\033[33m"
    reset = "\033[0m"

    def strip_ansi(text):
        """Remove ANSI color codes from text"""
        import re

        return re.sub(r"\033\[\d+m", "", text)

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
            f"{green}{timestamp}{reset}",
            f"{blue}function:{reset} {cyan}{func.__name__}{reset}",
            (
                f"{blue}execution_time_microseconds:{reset} "
                f"{yellow}{format_value(execution_time)}{reset}"
            ),
            f"{blue}total_requests:{reset} {yellow}{request_count}{reset}",
            f"{blue}total_trades:{reset} {yellow}{total_trades}{reset}",
            (
                f"{blue}average_batch_size:{reset} "
                f"{yellow}{format_value(average_batch_size)}{reset}"
            ),
            (
                f"{blue}average_time_per_request_microseconds:{reset} "
                f"{yellow}{format_value(average_time_per_request)}{reset}"
            ),
            (
                f"{blue}average_time_per_trade_microseconds:{reset} "
                f"{yellow}{format_value(average_time_per_trade)}{reset}"
            ),
        ]

        # Find the longest line length (accounting for ANSI escape codes)
        max_length = max(len(strip_ansi(line)) for line in log_lines)

        # Create the box
        box_top = f"╔{'═' * (max_length + 2)}╗"
        box_bottom = f"╚{'═' * (max_length + 2)}╝"

        # Format the log data with the box
        formatted_log = "\n".join(
            [
                box_top,
                *[f"║ {line}{' ' * (max_length - len(strip_ansi(line)))} ║" for line in log_lines],
                box_bottom,
            ]
        )

        logger.info(formatted_log)
        return result

    return wrapper
