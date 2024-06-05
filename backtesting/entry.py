import pandas as pd


def just_long(df: pd.DataFrame, i):
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] > df.at[i, "open"]:
        return volume >= volume_MA * 2 and df.at[i, "rsi"] <= 73

    return False


def just_short(df: pd.DataFrame, i) -> bool:
    volume = df.at[i, "volume"]
    volume_MA = df.at[i, "volume_MA"]

    if df.at[i, "close"] < df.at[i, "open"]:
        return volume >= volume_MA * 2 and df.at[i, "rsi"] >= 33

    return False
