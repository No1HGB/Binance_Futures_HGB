import numpy as np
import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# delta, diff, breakthrough 값 계산
def cal_coefficient(data: pd.DataFrame):
    df = data.copy()
    df["avg_price"] = (df["open"] + df["close"]) / 2

    df["avg_price_change"] = df["avg_price"].pct_change() * 100

    # Drop the first NaN value after computing percent change
    df = df.dropna()

    # 평균과 표준편차 계산
    mean_avg_price_change = df["avg_price_change"].mean()
    std_avg_price_change = df["avg_price_change"].std()

    # 평균+n*표준편차 및 평균+m*표준편차 값 계산
    plus_breakthrough = mean_avg_price_change + 1.12 * std_avg_price_change
    minus_breakthrough = mean_avg_price_change - 1.12 * std_avg_price_change

    return [plus_breakthrough, minus_breakthrough]


# 롱 진입 근거(돌파) 확인
def check_long(data: pd.DataFrame) -> bool:
    [plus_breakthrough, minus_breakthrough] = cal_coefficient(data)

    last_two = data.tail(2)
    if last_two.iloc[-1]["close"] > last_two.iloc[-1]["open"]:
        previous_avg = (last_two.iloc[-2]["open"] + last_two.iloc[-2]["close"]) / 2
        recent_avg = (last_two.iloc[-1]["open"] + last_two.iloc[-1]["close"]) / 2
        return (recent_avg - previous_avg) / previous_avg * 100 >= plus_breakthrough

    return False


# 숏 진입 근거(돌파) 확인
def check_short(data: pd.DataFrame) -> bool:
    [plus_breakthrough, minus_breakthrough] = cal_coefficient(data)

    last_two = data.tail(2)
    if last_two.iloc[-1]["close"] < last_two.iloc[-1]["open"]:
        previous_avg = (last_two.iloc[-2]["open"] + last_two.iloc[-2]["close"]) / 2
        recent_avg = (last_two.iloc[-1]["open"] + last_two.iloc[-1]["close"]) / 2
        return (recent_avg - previous_avg) / previous_avg * 100 <= minus_breakthrough

    return False


# RSI 계산
def calculate_rsi(df: pd.DataFrame) -> pd.DataFrame:
    # RSI 계산
    # 가격 변동 계산
    df["delta"] = df["close"] - df["close"].shift(1)

    # 이익과 손실 분리
    df["gain"] = np.where(df["delta"] >= 0, df["delta"], 0)
    df["loss"] = np.where(df["delta"] < 0, df["delta"].abs(), 0)

    # 평균 이익과 손실 계산
    df["avg_gain"] = df["gain"].ewm(alpha=1 / 14, min_periods=14).mean()
    df["avg_loss"] = df["loss"].ewm(alpha=1 / 14, min_periods=14).mean()

    # RSI 계산
    df["rsi"] = df["avg_gain"] / (df["avg_gain"] + df["avg_loss"]) * 100

    return df


def is_divergence(df: pd.DataFrame) -> list:
    # 가격 극대값과 극소값 찾기
    price_max_peaks = df[
        (df["close"] > df["close"].shift(1))
        & (df["close"] > df["close"].shift(-1))
        & (df["close"].shift(-1) > df["close"].shift(-2))
        & (df["close"].shift(1) > df["close"].shift(2))
    ]
    price_min_troughs = df[
        (df["close"] < df["close"].shift(1))
        & (df["close"] < df["close"].shift(-1))
        & (df["close"].shift(-1) < df["close"].shift(-2))
        & (df["close"].shift(1) < df["close"].shift(2))
    ]

    # RSI의 극대값과 극소값 찾기
    rsi_max_peaks = df[
        (df["rsi"] > df["rsi"].shift(1))
        & (df["rsi"] > df["rsi"].shift(-1))
        & (df["rsi"].shift(-1) > df["rsi"].shift(-2))
        & (df["rsi"].shift(1) > df["rsi"].shift(2))
    ]
    rsi_min_troughs = df[
        (df["rsi"] < df["rsi"].shift(1))
        & (df["rsi"] < df["rsi"].shift(-1))
        & (df["rsi"].shift(-1) < df["rsi"].shift(-2))
        & (df["rsi"].shift(1) < df["rsi"].shift(2))
    ]

    # 변수들
    last_index = df.index[-1]
    last_index_price_max = price_max_peaks.index[-1]
    last_index_price_min = price_min_troughs.index[-1]
    last_index_rsi_max = rsi_max_peaks.index[-1]
    last_index_rsi_min = rsi_min_troughs.index[-1]

    last_price_max = price_max_peaks.iloc[-1]["close"]
    last_two_price_max = price_max_peaks.iloc[-2]["close"]
    last_price_min = price_min_troughs.iloc[-1]["close"]
    last_two_price_min = price_min_troughs.iloc[-2]["close"]

    last_rsi_max = rsi_max_peaks.iloc[-1]["rsi"]
    last_two_rsi_max = rsi_max_peaks.iloc[-2]["rsi"]
    last_rsi_min = rsi_min_troughs.iloc[-1]["rsi"]
    last_two_rsi_min = rsi_min_troughs.iloc[-2]["rsi"]

    bullish = False
    bearish = False

    # bullish
    if last_index == (last_index_price_max + 2) and last_index == (
        last_index_rsi_max + 2
    ):
        if (
            last_price_max - last_two_price_max > 0
            and last_rsi_max - last_two_rsi_max < 0
        ):
            bearish = True
    # bearish
    elif last_index == (last_index_price_min + 2) and last_index == (
        last_index_rsi_min + 2
    ):
        if (
            last_price_min - last_two_price_min < 0
            and last_rsi_min - last_two_rsi_min > 0
        ):
            bullish = True

    return [bullish, bearish]
