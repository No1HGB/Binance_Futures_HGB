import pandas as pd
import Config


def cal_profit_price(entryPrice, side, symbol):
    profit_ratio = Config.profit_ratio

    if side == "BUY":
        stopPrice = entryPrice * (1 + profit_ratio / 100)

    elif side == "SELL":
        stopPrice = entryPrice * (1 - profit_ratio / 100)

    if symbol == "BTCUSDT":
        stopPrice = round(stopPrice, 1)
    elif symbol == "ETHUSDT":
        stopPrice = round(stopPrice, 2)

    return stopPrice


def cal_stop_price(entryPrice, side, symbol):
    stop_ratio = Config.stop_ratio

    if side == "BUY":
        stopPrice = entryPrice * (1 - stop_ratio / 100)

    elif side == "SELL":
        stopPrice = entryPrice * (1 + stop_ratio / 100)

    if symbol == "BTCUSDT":
        stopPrice = round(stopPrice, 1)
    elif symbol == "ETHUSDT":
        stopPrice = round(stopPrice, 2)

    return stopPrice


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


def ha_long(df: pd.DataFrame, v_coff) -> bool:
    last_row = df.iloc[-1]
    last_two = df.iloc[-2]

    return (
        last_row["ha_close"] > last_row["ha_open"]
        and last_row["volume"] >= last_row["volume_MA"] * v_coff
        and last_row["open"] < max(last_row["EMA20"], last_row["EMA50"])
        and last_row["close"] > last_row["open"]
        and last_row["avg_price"] > last_two["avg_price"]
    )


def ha_short(df: pd.DataFrame, v_coff) -> bool:
    last_row = df.iloc[-1]
    last_two = df.iloc[-2]

    return (
        last_row["ha_close"] < last_row["ha_open"]
        and last_row["volume"] >= last_row["volume_MA"] * v_coff
        and last_row["open"] > min(last_row["EMA20"], last_row["EMA50"])
        and last_row["close"] < last_row["open"]
        and last_row["avg_price"] < last_two["avg_price"]
    )


def ha_trend_long(df: pd.DataFrame, v_coff) -> bool:
    last_row = df.iloc[-1]
    last_two = df.iloc[-2]
    last_three = df.iloc[-3]

    return (
        last_row["EMA10"] > last_row["EMA20"]
        and last_row["EMA20"] > last_row["EMA50"]
        and last_row["volume"] >= last_row["volume_MA"] * v_coff
        and last_row["ha_close"] > last_row["ha_open"]
        and (
            last_two["ha_close"] < last_two["ha_open"]
            or last_three["ha_close"] < last_three["ha_open"]
        )
    )


def ha_trend_short(df: pd.DataFrame, v_coff) -> bool:
    last_row = df.iloc[-1]
    last_two = df.iloc[-2]
    last_three = df.iloc[-3]

    return (
        last_row["EMA10"] < last_row["EMA20"]
        and last_row["EMA20"] < last_row["EMA50"]
        and last_row["volume"] >= last_row["volume_MA"] * v_coff
        and last_row["ha_close"] < last_row["ha_open"]
        and (
            last_two["ha_close"] > last_two["ha_open"]
            or last_three["ha_close"] > last_three["ha_open"]
        )
    )


"""
def divergence(df: pd.DataFrame) -> list:
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

    # rsi 극값 인덱스
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
    last_rsi_min = rsi_min_troughs.iloc[-1]["rsi"]
    last_two_rsi_max = rsi_max_peaks.iloc[-2]["rsi"]
    last_two_rsi_min = rsi_min_troughs.iloc[-2]["rsi"]

    ema50 = df.iloc[-1]["EMA50"]
    high = df.iloc[-1]["high"]
    low = df.iloc[-1]["low"]
    last_seven = df.tail(7)
    pre_max_value = last_seven["up"][:].max()
    pre_min_value = last_seven["down"][:].min()

    divergence_long = False
    divergence_short = False

    # bearish
    if (
        last_index == (last_index_price_max + 3)
        and last_index_price_max == last_index_rsi_max
    ):
        if (
            last_price_max - last_two_price_max > 0
            and last_rsi_max - last_two_rsi_max < 0
            and low > ema50
            and pre_min_value > ema50
        ):
            divergence_short = True
    # bullish
    elif (
        last_index == (last_index_price_min + 3)
        and last_index_price_min == last_index_rsi_min
    ):
        if (
            last_price_min - last_two_price_min < 0
            and last_rsi_min - last_two_rsi_min > 0
            and high < ema50
            and pre_max_value < ema50
        ):
            divergence_long = True

    return [divergence_long, divergence_short]
"""
