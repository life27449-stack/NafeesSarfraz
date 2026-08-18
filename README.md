# 1-Min Forex Signal Bot (Python + MT5)

## What it does
- Reads M1 candles from MetaTrader 5.
- Calculates EMA 9/21/50, RSI and ATR.
- Produces UP/DOWN/WAIT signal with a score.
- Shows a live Streamlit dashboard.
- Includes a simple one-candle backtest.
- Defaults to signal-only mode.

## Install
1. Install MetaTrader 5 desktop and log in to a DEMO account first.
2. Install Python 3.10+.
3. Open a terminal in this folder:
   `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill MT5 connection details if needed.
5. Start:
   `streamlit run app.py`

## Important
AUTO_TRADE is intentionally not implemented in this starter build. Test signals and backtest first. A live execution layer should be added only after broker/account rules, symbol specifications, risk limits, and demo results are verified.

The M1 signal is a statistical/rule-based indicator, not a guaranteed prediction. Never use martingale to chase losses.
