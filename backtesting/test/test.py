import numpy as np
import pandas as pd
from fetch import fetch_data
from calculate import calculate_ema, calculate_values


df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=300)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df["EMA200"] = calculate_ema(df, 200)
df = calculate_values(df)

# 데이터 가공
df["delta"] = df["close"].pct_change() * 100
df["volume_R"] = df["volume"] / df["volume_MA"]
df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
df["time"] = df["open_time"].dt.time

df["up_tail"] = np.where(
    df["high"] > df[["open", "close"]].max(axis=1),
    abs(df["high"] - df[["open", "close"]].max(axis=1)) / abs(df["open"] - df["close"]),
    0,
)
df["down_tail"] = np.where(
    df["low"] < df[["open", "close"]].min(axis=1),
    abs(df["low"] - df[["open", "close"]].min(axis=1)) / abs(df["open"] - df["close"]),
    0,
)
# 과거 7개의 값을 새로운 열에 추가
for i in range(1, 120):
    df[f"delta{i}"] = df["delta"].shift(i)


df["EMA50_D"] = (df["close"] - df["EMA50"]) / df["close"] * 100
df["EMA200_D"] = (df["close"] - df["EMA200"]) / df["close"] * 100


df.drop(
    [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "EMA10",
        "EMA20",
        "EMA50",
        "EMA200",
        "rsi",
        "up",
        "down",
        "volume_MA",
        "avg_price",
        "ignore",
    ],
    axis=1,
    inplace=True,
)

print(df["open_time"])
