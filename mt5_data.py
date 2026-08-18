import MetaTrader5 as mt5
import pandas as pd

from config import (
    MT5_PATH,
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER,
)


def connect():
    kwargs = {}

    if MT5_PATH:
        kwargs["path"] = MT5_PATH

    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        kwargs["login"] = int(MT5_LOGIN)
        kwargs["password"] = MT5_PASSWORD
        kwargs["server"] = MT5_SERVER

    if not mt5.initialize(**kwargs):
        raise RuntimeError(
            f"MT5 initialize failed: {mt5.last_error()}"
        )


def get_bars(symbol, count=500):
    rates = mt5.copy_rates_from_pos(
        symbol,
        mt5.TIMEFRAME_M1,
        0,
        count
    )

    if rates is None or len(rates) < 100:
        raise RuntimeError(
            f"Could not load enough M1 bars: {mt5.last_error()}"
        )

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
        utc=True
    )

    return df


def shutdown():
    mt5.shutdown()