import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("KEY")
secret = os.getenv("SECRET")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
leverages = [5, 5, 3]
interval = "1h"  # 1h,4h,1d
ratio = 20  # margin ratio per balance (%)
profit_ratio = [5.7, 5.7, 7]  # take profit ratio for whole balance (%)
stop_ratio = 1  # stop loss ratio for whole balance (%)
