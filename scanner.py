import os
import time

import requests
import pandas as pd
from dotenv import load_dotenv

from signal_engine import calculate_signal


load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "TWELVE_DATA_API_KEY missing from .env"
    )


PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "AUD/USD": "AUD/USD",
    "USD/CAD": "USD/CAD",
}


def get_data(symbol, retries=3):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "1min",
        "outputsize": 100,
        "apikey": API_KEY,
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            if "values" not in data:
                raise RuntimeError(
                    data.get(
                        "message",
                        "No market data returned"
                    )
                )

            df = pd.DataFrame(data["values"])

            # Twelve Data returns newest candle first.
            # Signal engine expects chronological order.
            df = df.iloc[::-1].reset_index(drop=True)

            return df

        except Exception as e:
            last_error = e

            if attempt < retries:
                time.sleep(2)

    raise RuntimeError(
        f"{symbol}: failed after {retries} attempts: {last_error}"
    )


def scan():
    results = []

    for name, symbol in PAIRS.items():
        try:
            df = get_data(symbol)

            signal = calculate_signal(df)

            result = {
                "pair": name,
                "signal": signal.get("signal", "WAIT"),
                "score": signal.get("score", 0),
                "rsi": signal.get("rsi"),
                "ema_fast": signal.get("ema_fast"),
                "ema_slow": signal.get("ema_slow"),
                "atr": signal.get("atr"),
                "reasons": signal.get("reasons", []),
                "status": "OK",
            }

            results.append(result)

        except Exception as e:
            results.append({
                "pair": name,
                "signal": "ERROR",
                "score": 0,
                "rsi": None,
                "ema_fast": None,
                "ema_slow": None,
                "atr": None,
                "reasons": [],
                "status": str(e),
            })

    return results


if __name__ == "__main__":
    print()
    print("=== 1-MINUTE FOREX SCANNER ===")
    print()

    results = scan()

    for result in results:
        print(
            f"{result['pair']:8} | "
            f"{result['signal']:5} | "
            f"SCORE: {result['score']:3} | "
            f"RSI: {result['rsi']} | "
            f"{result['status']}"
        )