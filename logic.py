import numpy as np
import pandas as pd


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# 롱 진입 근거(돌파) 확인
def check_long(data: pd.DataFrame) -> bool:

    last_four = data.tail(4)
    if last_four.iloc[-1]["close"] > last_four.iloc[-1]["open"]:
        previous_ema_diff = last_four.iloc[-2]["EMA10"] - last_four.iloc[-2]["EMA20"]
        recent_ema_diff = last_four.iloc[-1]["EMA10"] - last_four.iloc[-1]["EMA20"]

        volume = last_four.iloc[-1]["volume"]
        volume_MA = last_four.iloc[-1]["volume_MA"] * 1.1

        return (
            (recent_ema_diff > previous_ema_diff)
            & (last_four.iloc[-1]["up"] > last_four.iloc[-2]["up"])
            & (last_four.iloc[-1]["up"] > last_four.iloc[-3]["up"])
            & (last_four.iloc[-1]["up"] > last_four.iloc[-4]["up"])
            & (volume < volume_MA)
        )

    return False


# 숏 진입 근거(돌파) 확인
def check_short(data: pd.DataFrame) -> bool:

    last_four = data.tail(4)
    if last_four.iloc[-1]["close"] < last_four.iloc[-1]["open"]:
        previous_ema_diff = last_four.iloc[-2]["EMA20"] - last_four.iloc[-2]["EMA10"]
        recent_ema_diff = last_four.iloc[-1]["EMA20"] - last_four.iloc[-1]["EMA10"]

        volume = last_four.iloc[-1]["volume"]
        volume_MA = last_four.iloc[-1]["volume_MA"] * 1.1

        return (
            (recent_ema_diff > previous_ema_diff)
            & (last_four.iloc[-1]["down"] < last_four.iloc[-2]["down"])
            & (last_four.iloc[-1]["down"] < last_four.iloc[-3]["down"])
            & (last_four.iloc[-1]["down"] < last_four.iloc[-4]["down"])
            & (volume < volume_MA)
        )

    return False


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

    # 원래 DataFrame에 'rsi', 'up', 'down', "volume_MA", "avg_price" 추가
    df["rsi"] = temp_df["rsi"]
    df["up"] = np.maximum(df["open"], df["close"])
    df["down"] = np.minimum(df["open"], df["close"])
    df["volume_MA"] = df["volume"].rolling(window=50).mean()
    df["avg_price"] = (df["open"] + df["close"]) / 2

    return df


def is_divergence(df: pd.DataFrame) -> list:
    # 가격 극대값과 극소값 찾기
    price_max_peaks = df[
        (df["avg_price"] > df["avg_price"].shift(1))
        & (df["avg_price"] > df["avg_price"].shift(-1))
        & (df["avg_price"] > df["avg_price"].shift(2))
        & (df["avg_price"] > df["avg_price"].shift(-2))
    ]
    price_min_troughs = df[
        (df["avg_price"] < df["avg_price"].shift(1))
        & (df["avg_price"] < df["avg_price"].shift(-1))
        & (df["avg_price"] < df["avg_price"].shift(2))
        & (df["avg_price"] < df["avg_price"].shift(-2))
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

    # 가격 극값 인덱스 RSI 기준으로 통일
    if price_max_peaks.iloc[-1]["open"] > price_max_peaks.iloc[-1]["close"]:
        last_index_price_max = price_max_peaks.index[-1] - 1
    else:
        last_index_price_max = price_max_peaks.index[-1]
    if price_min_troughs.iloc[-1]["open"] < price_max_peaks.iloc[-1]["close"]:
        last_index_price_min = price_min_troughs.index[-1] - 1
    else:
        last_index_price_min = price_min_troughs.index[-1]

    last_index_rsi_max = rsi_max_peaks.index[-1]
    last_index_rsi_min = rsi_min_troughs.index[-1]

    # 가격 결정
    last_price_max = max(
        price_max_peaks.iloc[-1]["open"], price_max_peaks.iloc[-1]["close"]
    )
    last_two_price_max = max(
        price_max_peaks.iloc[-2]["open"], price_max_peaks.iloc[-2]["close"]
    )
    last_price_min = min(
        price_min_troughs.iloc[-1]["open"], price_min_troughs.iloc[-1]["close"]
    )
    last_two_price_min = min(
        price_min_troughs.iloc[-2]["open"], price_min_troughs.iloc[-2]["close"]
    )

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


def cal_stop_price(entryPrice, side, symbol, positionAmt, balance):

    entry_minus_stop_abs = (
        (balance * 1.5 / 100 - positionAmt * 0.002 / 100) / positionAmt * entryPrice
    )

    if side == "BUY":
        stopPrice = entryPrice - entry_minus_stop_abs

    elif side == "SELL":
        stopPrice = entryPrice + entry_minus_stop_abs

    if symbol == "BTCUSDT":
        stopPrice = round(stopPrice, 1)
    elif symbol == "ETHUSDT":
        stopPrice = round(stopPrice, 2)
    elif symbol == "SOLUSDT":
        stopPrice = round(stopPrice, 3)

    return stopPrice
