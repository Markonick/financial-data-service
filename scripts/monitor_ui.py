import asyncio
import time

from typing import Dict

import httpx
import pandas as pd
import streamlit as st

# Constants
REFRESH_RATE = 1  # seconds
SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "FB", "BRK.A", "V", "JNJ", "WMT"]
MAX_WINDOW_SIZE = 10**8  # The maximum window size


async def get_stats(client: httpx.AsyncClient, symbol: str, k: int):
    try:
        response = await client.get(f"http://localhost:8000/stats/{symbol}/{k}")
        return response.json() if response.status_code == 200 else None
    except:
        return None


async def fetch_all_stats():
    async with httpx.AsyncClient() as client:
        active_symbols = set()
        stats_data: Dict[str, dict] = {}

        for symbol in SYMBOLS:
            stats = await get_stats(client, symbol, 1)
            if stats:
                active_symbols.add(symbol)
                stats_data[symbol] = {"window_stats": [], "max_window": None}

                for k in range(1, 9):
                    stats = await get_stats(client, symbol, k)
                    if stats:
                        window_size = 10**k
                        stats_data[symbol]["window_stats"].append(
                            {
                                "window": f"10^{k}",
                                "min": stats["min"],
                                "max": stats["max"],
                                "last": stats["last"],
                                "avg": stats["avg"],
                                "var": stats["var"],
                                "values": stats["values"],
                            }
                        )

                        if k == 8:
                            stats_data[symbol]["max_window"] = {
                                "current_size": stats["values"],
                                "max_size": MAX_WINDOW_SIZE,
                                "last": stats["last"],
                            }

        return active_symbols, stats_data


def main():
    st.set_page_config(page_title="Financial Data Monitor", layout="wide")
    st.title("Financial Data Service Monitor")

    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Uptime (seconds)", int(time.time() - st.session_state.start_time))

    active_symbols, stats_data = asyncio.run(fetch_all_stats())

    with col2:
        st.metric("Active Symbols", len(active_symbols))

    with col3:
        st.metric("Total Windows", len(active_symbols) * 8)

    # Combined Active Symbols and Detailed Stats
    st.subheader("Symbol Statistics")

    # Create pairs of symbols for two-column layout
    symbol_pairs = [
        (SYMBOLS[i], SYMBOLS[i + 1]) if i + 1 < len(SYMBOLS) else (SYMBOLS[i], None)
        for i in range(0, len(SYMBOLS), 2)
    ]

    for symbol1, symbol2 in symbol_pairs:
        col1, col2 = st.columns(2)

        # First symbol
        with col1:
            if symbol1 in active_symbols and symbol1 in stats_data:
                # Active symbol pill
                st.success(symbol1)

                # Progress bar
                max_window = stats_data[symbol1]["max_window"]
                if max_window:
                    current = max_window["current_size"]
                    progress = min(1.0, current / MAX_WINDOW_SIZE)
                    percentage = progress * 100
                    st.progress(progress, text=f"{percentage:.1f}%")

                # Stats table
                df = pd.DataFrame(stats_data[symbol1]["window_stats"])
                df = df.set_index("window")
                st.dataframe(
                    df.style.format(
                        {
                            "min": "{:.2f}",
                            "max": "{:.2f}",
                            "last": "{:.2f}",
                            "avg": "{:.2f}",
                            "var": "{:.2f}",
                            "values": "{:,.0f}",
                        }
                    ),
                    use_container_width=True,
                )
            else:
                st.error(symbol1)

        # Second symbol (if it exists)
        with col2:
            if symbol2:  # Check if there is a second symbol (for odd number of symbols)
                if symbol2 in active_symbols and symbol2 in stats_data:
                    # Active symbol pill
                    st.success(symbol2)

                    # Progress bar
                    max_window = stats_data[symbol2]["max_window"]
                    if max_window:
                        current = max_window["current_size"]
                        progress = min(1.0, current / MAX_WINDOW_SIZE)
                        percentage = progress * 100
                        st.progress(progress, text=f"{percentage:.1f}%")

                    # Stats table
                    df = pd.DataFrame(stats_data[symbol2]["window_stats"])
                    df = df.set_index("window")
                    st.dataframe(
                        df.style.format(
                            {
                                "min": "{:.2f}",
                                "max": "{:.2f}",
                                "last": "{:.2f}",
                                "avg": "{:.2f}",
                                "var": "{:.2f}",
                                "values": "{:,.0f}",
                            }
                        ),
                        use_container_width=True,
                    )
                else:
                    st.error(symbol2)

        st.divider()

    time.sleep(REFRESH_RATE)
    st.rerun()


if __name__ == "__main__":
    main()
