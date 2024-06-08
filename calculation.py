import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# RSI 계산
def calculate_values(df: pd.DataFrame) -> pd.DataFrame:
    df["volume_MA"] = df["volume"].rolling(window=50).mean()
    df["avg_price"] = (df["open"] + df["close"]) / 2

    return df
