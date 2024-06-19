import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("KEY")
secret = os.getenv("SECRET")

symbols = ["BTCUSDT", "ETHUSDT"]
leverage = 5
interval = "1h"  # 1h,4h,1d
ratio = 25  # margin ratio per balance (%)
profit_ratio = 2  # take profit ratio for price (%)
stop_ratio = 1.5  # stop loss ratio for price (%)
