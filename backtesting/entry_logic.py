import pandas as pd


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


def reverse_long(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "close"] > df.at[i, "open"]
        and df.at[i, "close"] < df.at[i, "EMA50"]
        and (
            df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
            or (
                df.at[i - 1, "volume"] >= df.at[i - 1, "volume_MA"] * v_coff
                and df.at[i - 1, "close"] > df.at[i - 1, "open"]
            )
        )
        and df.at[i, "avg_price"] > df.at[i - 1, "avg_price"]
    )


def reverse_short(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "close"] < df.at[i, "open"]
        and df.at[i, "close"] > df.at[i, "EMA50"]
        and (
            df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
            or (
                df.at[i - 1, "volume"] >= df.at[i - 1, "volume_MA"] * v_coff
                and df.at[i - 1, "close"] < df.at[i - 1, "open"]
            )
        )
        and df.at[i, "avg_price"] < df.at[i - 1, "avg_price"]
    )


def middle_long(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "close"] > df.at[i, "open"]
        and df.at[i, "close"] > df.at[i, "EMA50"]
        and df.at[i, "open"] < df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and max(df.at[i - 1, "open"], df.at[i - 1, "close"]) < df.at[i - 1, "EMA50"]
    )


def middle_short(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "close"] < df.at[i, "open"]
        and df.at[i, "close"] < df.at[i, "EMA50"]
        and df.at[i, "open"] > df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and min(df.at[i - 1, "open"], df.at[i - 1, "close"]) > df.at[i - 1, "EMA50"]
    )


# 하이킨아시 기반 전략
def ha_trend_long(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "EMA10"] > df.at[i, "EMA20"]
        and df.at[i, "EMA20"] > df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and df.at[i, "ha_close"] > df.at[i, "ha_open"]
        and df.at[i - 1, "ha_close"] < df.at[i - 1, "ha_open"]
    )


def ha_trend_short(df: pd.DataFrame, i, v_coff) -> bool:

    return (
        df.at[i, "EMA10"] < df.at[i, "EMA20"]
        and df.at[i, "EMA20"] < df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and df.at[i, "ha_close"] < df.at[i, "ha_open"]
        and df.at[i - 1, "ha_close"] > df.at[i - 1, "ha_open"]
    )


def simple_long(df: pd.DataFrame, i) -> bool:
    return (
        df.at[i, "close"] > df.at[i, "open"]
        and df.at[i, "avg_price"] > df.at[i - 1, "avg_price"]
        and df.at[i, "close"] > df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * 1.5
    )


def simple_short(df: pd.DataFrame, i) -> bool:
    return (
        df.at[i, "close"] < df.at[i, "open"]
        and df.at[i, "avg_price"] < df.at[i - 1, "avg_price"]
        and df.at[i, "close"] < df.at[i, "EMA50"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * 1.5
    )


def ha_long(df: pd.DataFrame, i, v_coff) -> bool:
    return (
        df.at[i, "ha_close"] > df.at[i, "ha_open"]
        and (df.at[i, "ha_close"] + df.at[i, "ha_open"]) / 2
        > (df.at[i - 1, "ha_close"] + df.at[i - 1, "ha_open"]) / 2
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
    )


def ha_short(df: pd.DataFrame, i, v_coff) -> bool:
    return (
        df.at[i, "ha_close"] < df.at[i, "ha_open"]
        and (df.at[i, "ha_close"] + df.at[i, "ha_open"]) / 2
        < (df.at[i - 1, "ha_close"] + df.at[i - 1, "ha_open"]) / 2
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
    )


def maker_long(df: pd.DataFrame, i, v_coff) -> bool:
    return (
        df.at[i, "close"] > df.at[i, "open"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and df.at[i, "maker_buy"] < df.at[i, "taker_buy"]
        and df.at[i, "avg_price"] > df.at[i - 1, "avg_price"]
    )


def maker_short(df: pd.DataFrame, i, v_coff) -> bool:
    return (
        df.at[i, "close"] < df.at[i, "open"]
        and df.at[i, "volume"] >= df.at[i, "volume_MA"] * v_coff
        and df.at[i, "maker_buy"] > df.at[i, "taker_buy"]
        and df.at[i, "avg_price"] < df.at[i - 1, "avg_price"]
    )


def stop_long(df: pd.DataFrame, i) -> bool:
    # 비정상 롱
    if df.at[i, "close"] > df.at[i, "open"]:
        return df.at[i, "maker_buy"] > df.at[i, "taker_buy"]
    # 정상 숏
    elif df.at[i, "close"] < df.at[i, "open"]:
        return (
            df.at[i, "maker_buy"] > df.at[i, "taker_buy"]
            and df.at[i, "avg_price"] < df.at[i - 1, "avg_price"]
        )
    return False


def stop_short(df: pd.DataFrame, i) -> bool:
    # 비정상 숏
    if df.at[i, "close"] < df.at[i, "open"]:
        return df.at[i, "maker_buy"] < df.at[i, "taker_buy"]
    # 정상 롱
    elif df.at[i, "close"] > df.at[i, "open"]:
        return (
            df.at[i, "maker_buy"] < df.at[i, "taker_buy"]
            and df.at[i, "avg_price"] > df.at[i - 1, "avg_price"]
        )
    return False
