import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fetch import fetch_data, fetch_one_data
from calculate import calculate_ema
import datetime


now = datetime.datetime.now(datetime.UTC)
end_datetime = now.replace(
    hour=0, minute=0, second=0, microsecond=0
) - datetime.timedelta(days=1)
endTime = int(end_datetime.timestamp() * 1000)

df = fetch_data("BTCUSDT", "1h", 1000)
df["delta"] = (df["close"] - df["open"]) / df["open"] * 100
df["delta_abs"] = abs(df["close"] - df["open"]) / df["open"] * 100
df["delta_mean"] = df["delta_abs"].rolling(window=50).mean()
alpha = 2 / (50 + 1)
df["delta_ema"] = df["delta_abs"].ewm(alpha=alpha, adjust=False).mean()

print(df[["delta", "delta_ema", "delta_mean"]].tail(30))
