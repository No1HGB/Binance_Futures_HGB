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


def reverse_long(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] > df.at[i, "open"]:
        return (
            volume >= volume_MA * 1.7
            and df.at[i, "avg_price"] > df.at[i - 1, "avg_price"]
            and df.at[i, "close"] < df.at[i, "EMA50"]
        )

    return False


def reverse_short(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] < df.at[i, "open"]:
        return (
            volume >= volume_MA * 1.7
            and df.at[i, "avg_price"] < df.at[i - 1, "avg_price"]
            and df.at[i, "close"] > df.at[i, "EMA50"]
        )

    return False


def qullamaggi_long(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if i >= 7:
        up_max = df["up"][i - 7 : i].max()

    if df.at[i, "close"] > df.at[i, "open"]:
        return (
            df.at[i, "close"] > up_max
            and volume >= volume_MA * 1.5
            and df.at[i, "close"] > df.at[i, "EMA200"]
        )

    return False


def qullamaggi_short(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if i >= 7:
        down_min = df["down"][i - 7 : i].min()

    if df.at[i, "close"] < df.at[i, "open"]:
        return (
            df.at[i, "close"] < down_min
            and volume >= volume_MA * 1.5
            and df.at[i, "close"] < df.at[i, "EMA200"]
        )

    return False


def conti_long(df: pd.DataFrame, i) -> bool:

    if (
        df.at[i, "close"] > df.at[i, "open"]
        and df.at[i - 1, "close"] > df.at[i - 1, "open"]
    ):
        return (
            df.at[i, "volume"] >= df.at[i, "volume_MA"] * 1.2
            and df.at[i - 1, "volume"] >= df.at[i - 1, "volume_MA"] * 1.2
        )

    return False


def conti_short(df: pd.DataFrame, i) -> bool:

    if (
        df.at[i, "close"] < df.at[i, "open"]
        and df.at[i - 1, "close"] < df.at[i - 1, "open"]
    ):
        return (
            df.at[i, "volume"] >= df.at[i, "volume_MA"] * 1.2
            and df.at[i - 1, "volume"] >= df.at[i - 1, "volume_MA"] * 1.2
        )

    return False
