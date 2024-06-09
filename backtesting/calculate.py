import numpy as np
import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# RSI 계산
def calculate_values(df: pd.DataFrame) -> pd.DataFrame:
    # 원본 DataFrame을 변경하지 않기 위해 복사본을 사용
    temp_df = df.copy()

    # 가격 변동 계산
    temp_df["delta"] = temp_df["close"] - temp_df["close"].shift(1)

    # 이익과 손실 분리
    temp_df["gain"] = np.where(temp_df["delta"] >= 0, temp_df["delta"], 0)
    temp_df["loss"] = np.where(temp_df["delta"] < 0, temp_df["delta"].abs(), 0)

    # 평균 이익과 손실 계산
    temp_df["avg_gain"] = temp_df["gain"].ewm(alpha=1 / 14, min_periods=14).mean()
    temp_df["avg_loss"] = temp_df["loss"].ewm(alpha=1 / 14, min_periods=14).mean()

    # RSI 계산
    temp_df["rsi"] = (
        temp_df["avg_gain"] / (temp_df["avg_gain"] + temp_df["avg_loss"]) * 100
    )

    # 원래 DataFrame에 'rsi',"up","down","volume_MA","avg_price" 추가
    df["rsi"] = temp_df["rsi"]
    df["up"] = np.maximum(df["open"], df["close"])
    df["down"] = np.minimum(df["open"], df["close"])
    df["up_tail"] = df.apply(
        lambda row: (
            0
            if row["close"] == row["open"]
            else abs(row["high"] - row["up"]) / abs(row["open"] - row["close"])
        ),
        axis=1,
    )
    df["down_tail"] = df.apply(
        lambda row: (
            0
            if row["close"] == row["open"]
            else abs(row["low"] - row["down"]) / abs(row["open"] - row["close"])
        ),
        axis=1,
    )
    df["volume_MA"] = df["volume"].rolling(window=50).mean()
    df["avg_price"] = (df["open"] + df["close"]) / 2

    return df
