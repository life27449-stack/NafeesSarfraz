import numpy as np
import pandas as pd

def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df, n=14):
    h, l, c = df.high, df.low, df.close
    tr = pd.concat([(h-l), (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()

def add_indicators(df):
    x = df.copy()
    x["ema9"] = ema(x.close, 9)
    x["ema21"] = ema(x.close, 21)
    x["ema50"] = ema(x.close, 50)
    x["rsi"] = rsi(x.close, 14)
    x["atr"] = atr(x, 14)
    x["mom"] = x.close.pct_change(5) * 100
    return x.dropna().reset_index(drop=True)

def signal(df, min_score=70):
    x = add_indicators(df)
    a, b = x.iloc[-1], x.iloc[-2]
    up = down = 0.0
    reasons = []

    if a.ema9 > a.ema21: up += 25; reasons.append("EMA9>EMA21")
    else: down += 25; reasons.append("EMA9<EMA21")
    if a.ema21 > a.ema50: up += 20
    else: down += 20
    if 50 < a.rsi < 70: up += 20; reasons.append("RSI bullish zone")
    elif 30 < a.rsi < 50: down += 20; reasons.append("RSI bearish zone")
    if a.close > a.ema9: up += 15
    else: down += 15
    if a.mom > 0: up += 20
    else: down += 20

    score = max(up, down)
    direction = "UP" if up > down else "DOWN" if down > up else "WAIT"
    if score < min_score:
        direction = "WAIT"
    return {
        "direction": direction,
        "score": round(score, 1),
        "up_score": round(up, 1),
        "down_score": round(down, 1),
        "price": float(a.close),
        "rsi": round(float(a.rsi), 2),
        "atr": float(a.atr),
        "candle_time": a.time,
        "reasons": reasons
    }
