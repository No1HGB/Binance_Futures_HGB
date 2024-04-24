import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("KEY")
secret = os.getenv("SECRET")

symbol = "BTCUSDT"
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
interval = "1h"  # 1h,4h,1d
margin = 25  # ratio per balance (%)
