import os
from dotenv import load_dotenv
load_dotenv()

SYMBOL = os.getenv("SYMBOL", "EURUSD")
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "0.5"))
MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "2.0"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "70"))
AUTO_TRADE = os.getenv("AUTO_TRADE", "false").lower() == "true"
MT5_LOGIN = os.getenv("MT5_LOGIN", "")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")
MT5_PATH = os.getenv("MT5_PATH", "")
