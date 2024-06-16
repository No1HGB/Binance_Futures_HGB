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


def reverse_long(data: pd.DataFrame, i, v_coff=1.5) -> bool:
    last_row = data.iloc[-1]
    last_two = data.iloc[-2]
    return (
        last_row["close"] > last_row["open"]
        and last_row["close"] < last_row["EMA50"]
        and (
            last_row["volume"] >= last_row["volume_MA"] * v_coff
            or (
                last_two["volume"] >= last_two["volume_MA"] * v_coff
                and last_two["close"] > last_two["open"]
            )
        )
        and last_row["avg_price"] > last_two["avg_price"]
    )


def reverse_short(data: pd.DataFrame, i, v_coff) -> bool:
    last_row = data.iloc[-1]
    last_two = data.iloc[-2]
    return (
        last_row["close"] < last_row["open"]
        and last_row["close"] > last_row["EMA50"]
        and (
            last_row["volume"] >= last_row["volume_MA"] * v_coff
            or (
                last_two["volume"] >= last_two["volume_MA"] * v_coff
                and last_two["close"] < last_two["open"]
            )
        )
        and last_row["avg_price"] < last_two["avg_price"]
    )


def just_long(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] > df.at[i, "open"]:
        return (
            volume >= volume_MA * 1.5
            and df.at[i, "close"] > df.at[i, "EMA50"]
            and df.at[i, "open"] < df.at[i, "EMA50"]
        )

    return False


def just_short(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] < df.at[i, "open"]:
        return (
            volume >= volume_MA * 1.5
            and df.at[i, "close"] < df.at[i, "EMA50"]
            and df.at[i, "open"] > df.at[i, "EMA50"]
        )

    return False


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
