import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# 필요 수치 계산
def calculate_values(df: pd.DataFrame) -> pd.DataFrame:
    df["volume_MA"] = df["volume"].rolling(window=50).mean()
    df["avg_price"] = (df["open"] + df["close"]) / 2

    # 하이킨아시
    df["ha_close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4

    df["ha_open"] = 0.0
    df.at[0, "ha_open"] = df.iloc[0]["open"]

    df["ha_high"] = 0.0
    df["ha_low"] = 0.0

    for i in range(1, len(df)):
        df.at[i, "ha_open"] = (df.at[i - 1, "ha_open"] + df.at[i - 1, "ha_close"]) / 2
        df.at[i, "ha_high"] = max(
            df.at[i, "high"], df.at[i, "ha_open"], df.at[i, "ha_close"]
        )
        df.at[i, "ha_low"] = min(
            df.at[i, "low"], df.at[i, "ha_open"], df.at[i, "ha_close"]
        )

    df.at[0, "ha_high"] = df.at[0, "high"]
    df.at[0, "ha_low"] = df.at[0, "low"]

    return df
