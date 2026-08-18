import pandas as pd
import ta


def calculate_signal(df):
    df = df.copy()

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().reset_index(drop=True)

    if len(df) < 50:
        return {
            "signal": "WAIT",
            "score": 0,
            "reason": "Not enough candles"
        }

    # Last candle may still be forming.
    # Use the previous candle as the closed candle.
    closed = df.iloc[:-1].copy()

    if len(closed) < 50:
        return {
            "signal": "WAIT",
            "score": 0,
            "reason": "Not enough closed candles"
        }

    closed["ema_fast"] = ta.trend.ema_indicator(
        closed["close"], window=9
    )

    closed["ema_slow"] = ta.trend.ema_indicator(
        closed["close"], window=21
    )

    closed["rsi"] = ta.momentum.rsi(
        closed["close"], window=14
    )

    macd = ta.trend.MACD(closed["close"])

    closed["macd"] = macd.macd()
    closed["macd_signal"] = macd.macd_signal()

    closed["atr"] = ta.volatility.average_true_range(
        closed["high"],
        closed["low"],
        closed["close"],
        window=14
    )

    closed = closed.dropna().reset_index(drop=True)

    if len(closed) < 2:
        return {
            "signal": "WAIT",
            "score": 0,
            "reason": "Indicators not ready"
        }

    last = closed.iloc[-1]
    previous_close = closed["close"].iloc[-2]

    score_up = 0
    score_down = 0
    reasons = []

    # EMA trend
    if last["ema_fast"] > last["ema_slow"]:
        score_up += 25
        reasons.append("EMA bullish")
    elif last["ema_fast"] < last["ema_slow"]:
        score_down += 25
        reasons.append("EMA bearish")

    # RSI
    if 50 < last["rsi"] < 70:
        score_up += 20
        reasons.append("RSI bullish")
    elif 30 < last["rsi"] < 50:
        score_down += 20
        reasons.append("RSI bearish")

    # MACD
    if last["macd"] > last["macd_signal"]:
        score_up += 25
        reasons.append("MACD bullish")
    elif last["macd"] < last["macd_signal"]:
        score_down += 25
        reasons.append("MACD bearish")

    # Closed candle direction
    if last["close"] > last["open"]:
        score_up += 15
        reasons.append("Bullish candle")
    elif last["close"] < last["open"]:
        score_down += 15
        reasons.append("Bearish candle")

    # Momentum
    if last["close"] > previous_close:
        score_up += 15
        reasons.append("Positive momentum")
    elif last["close"] < previous_close:
        score_down += 15
        reasons.append("Negative momentum")

    if score_up >= 70 and score_up > score_down:
        signal = "UP"
        score = score_up
    elif score_down >= 70 and score_down > score_up:
        signal = "DOWN"
        score = score_down
    else:
        signal = "WAIT"
        score = max(score_up, score_down)

    return {
        "signal": signal,
        "score": int(score),
        "rsi": round(float(last["rsi"]), 2),
        "ema_fast": round(float(last["ema_fast"]), 5),
        "ema_slow": round(float(last["ema_slow"]), 5),
        "atr": round(float(last["atr"]), 6),
        "reasons": reasons
    }