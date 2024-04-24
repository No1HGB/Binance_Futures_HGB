import pandas as pd
import talib


# EMA 계산
def calculate_ema(data: pd.DataFrame, days, smoothing=2):
    alpha = smoothing / (days + 1)
    return data["close"].ewm(alpha=alpha, adjust=False).mean()


# 4개의 가격 박스권 여부 검사
def check_box(data: pd.DataFrame, interval: str) -> bool:
    if interval == "1h":
        delta = 0.17
        diff = 0.33
    elif interval == "4h":
        delta = 0.24
        diff = 0.7
    elif interval == "1d":
        delta = 0.7
        diff = 2

    last_four = data.tail(4)
    last_four["average_price"] = last_four[["open", "close"]].astype(float).mean(axis=1)
    change_rates = last_four["average_price"].pct_change() * 100
    # 인접한 평균값들의 변화율이 delta% 이하인지 확인
    change_rate_condition = (change_rates.abs().dropna() <= delta).all()

    # open과 close 값들 중 최댓값과 최솟값의 차이가 diff% 이하인지 검사
    max_value = last_four[["open", "close"]].values.max()
    min_value = last_four[["open", "close"]].values.min()
    difference_condition = ((max_value - min_value) / min_value * 100) <= diff

    # 두 조건이 모두 만족하면 True, 그렇지 않으면 False 반환
    return change_rate_condition and difference_condition


# 롱 진입 근거(돌파) 확인
def check_long(data: pd.DataFrame, interval: str) -> bool:
    if interval == "1h":
        breakthrough = 0.5
    elif interval == "4h":
        breakthrough = 1
    elif interval == "1d":
        breakthrough = 2

    last_two = data.tail(2)
    if last_two.iloc[-1]["close"] > last_two.iloc[-1]["open"]:
        previous_high = max(last_two.iloc[-2]["open"], last_two.iloc[-2]["close"])
        recent_close = last_two.iloc[-1]["close"]
        return (recent_close - previous_high) / previous_high * 100 >= breakthrough

    return False


# 숏 진입 근거(돌파) 확인
def check_short(data: pd.DataFrame, interval: str) -> bool:
    if interval == "1h":
        breakthrough = 0.5
    elif interval == "4h":
        breakthrough = 1
    elif interval == "1d":
        breakthrough = 2

    last_two = data.tail(2)
    if last_two.iloc[-1]["close"] < last_two.iloc[-1]["open"]:
        previous_low = min(last_two.iloc[-2]["open"], last_two.iloc[-2]["close"])
        recent_close = last_two.iloc[-1]["close"]
        return (recent_close - previous_low) / previous_low * 100 >= breakthrough

    return False


# RSI 다이버전스(임시)
def calculate_rsi_divergences(df):
    # RSI 계산
    close_prices = df["close"].values
    rsi = talib.RSI(close_prices, timeperiod=14)
    df["rsi"] = rsi

    # 가격의 극대값과 극소값 찾기
    max_peaks = df[
        (df["close"] > df["close"].shift(1)) & (df["close"] > df["close"].shift(-1))
    ]
    min_troughs = df[
        (df["close"] < df["close"].shift(1)) & (df["close"] < df["close"].shift(-1))
    ]

    # RSI의 극대값과 극소값 찾기
    rsi_max_peaks = df[
        (df["rsi"] > df["rsi"].shift(1)) & (df["rsi"] > df["rsi"].shift(-1))
    ]
    rsi_min_troughs = df[
        (df["rsi"] < df["rsi"].shift(1)) & (df["rsi"] < df["rsi"].shift(-1))
    ]
