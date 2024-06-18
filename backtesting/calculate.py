import numpy as np
import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# RSI 계산
def calculate_values(df: pd.DataFrame) -> pd.DataFrame:
    df["up"] = np.maximum(df["open"], df["close"])
    df["down"] = np.minimum(df["open"], df["close"])
    df["volume_MA"] = df["volume"].rolling(window=50).mean()
    df["avg_price"] = (df["open"] + df["close"]) / 2
    df["maker_buy"] = df["volume"] - df["taker_buy"]
    df["volume_R"] = df["volume"] / df["volume_MA"]

    # 가격 극대값과 극소값 찾기

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


def cal_resistance(df: pd.DataFrame):
    # df의 마지막 127개 행 선택
    df_tail = df.tail(127)

    price_max_peaks = df_tail[
        (df_tail["avg_price"] > df_tail["avg_price"].shift(1))
        & (df_tail["avg_price"] > df_tail["avg_price"].shift(-1))
        & (df_tail["avg_price"].shift(1) > df_tail["avg_price"].shift(2))
        & (df_tail["avg_price"].shift(-1) > df_tail["avg_price"].shift(-2))
    ]

    if price_max_peaks.empty:
        return 0.0

    # 평균 값을 담기 위한 리스트 초기화
    volumes_prices = []

    # 조건을 만족하는 행들의 인덱스 리스트 생성
    true_indices = price_max_peaks.index

    for index in true_indices:
        # 현재 행, 이전 행, 다음 행의 volume_R 값의 평균 계산
        volume_mean = df.loc[index - 1 : index + 1, "volume_R"].mean()
        volumes_prices.append((volume_mean, df.loc[index, ["close", "open"]].max()))

    # 가장 최근의 가격 값 중 거래량 비율이 1보다 큰 값
    for element in reversed(volumes_prices):
        if element[0] > 1:
            return element[1]

    return 0.0


def cal_support(df: pd.DataFrame):
    # df의 마지막 127개 행 선택
    df_tail = df.tail(127)

    price_min_troughs = df_tail[
        (df_tail["avg_price"] < df_tail["avg_price"].shift(1))
        & (df_tail["avg_price"] < df_tail["avg_price"].shift(-1))
        & (df_tail["avg_price"].shift(1) < df_tail["avg_price"].shift(2))
        & (df_tail["avg_price"].shift(-1) < df_tail["avg_price"].shift(-2))
    ]

    if price_min_troughs.empty:
        return float("inf")

    # 평균 값을 담기 위한 리스트 초기화
    volumes_prices = []

    # 조건을 만족하는 행들의 인덱스 리스트 생성
    true_indices = price_min_troughs.index

    for index in true_indices:
        # 현재 행, 이전 행, 다음 행의 volume_R 값의 평균 계산
        volume_mean = df.loc[index - 1 : index + 1, "volume_R"].mean()
        volumes_prices.append((volume_mean, df.loc[index, ["close", "open"]].min()))

    # 가장 최근의 가격 값 중 거래량 비율이 1보다 큰 값
    for element in reversed(volumes_prices):
        if element[0] > 1:
            return element[1]

    return float("inf")
