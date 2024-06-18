import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pandas as pd
import datetime
from binance.um_futures import UMFutures
from calculate import calculate_ema, calculate_values
from entry_logic import (
    just_long,
    just_short,
    reverse_long,
    reverse_short,
    middle_long,
    middle_short,
    ha_trend_long,
    ha_trend_short,
    simple_long,
    simple_short,
    ha_long,
    ha_short,
    maker_long,
    maker_short,
    stop_long,
    stop_short,
)


def fetch_one_data(symbol, interval, endTime, limit):
    client = UMFutures()
    bars = client.klines(
        symbol=symbol,
        interval=interval,
        endTime=endTime,
        limit=limit,
    )
    df = pd.DataFrame(
        bars,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    df.drop(
        [
            "close_time",
            "quote_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
        axis=1,
        inplace=True,
    )
    df.rename(columns={"taker_buy_base_asset_volume": "taker_buy"}, inplace=True)

    # 모든 열을 숫자형으로 변환
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # "open_time" 열을 datetime 형식으로 변환
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    return df


def fetch_data(symbol, interval, numbers):
    now = datetime.datetime.now(datetime.UTC)
    end_datetime = now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(
        hours=1
    )
    endTime = int(end_datetime.timestamp() * 1000)
    data = []

    while numbers > 0:
        if numbers < 1500:
            num = numbers
        else:
            num = 1500

        df = fetch_one_data(symbol, interval, endTime, num)
        data.insert(0, df)
        endTime -= int(datetime.timedelta(hours=num).total_seconds() * 1000)
        numbers -= num

    data_combined = pd.concat(data)
    data_combined.reset_index(drop=True, inplace=True)

    return data_combined


"""
startDate_str = input()
endDate_str = input()
startDate_time_obj = datetime.datetime.strptime(startDate_str, "%y-%m-%d %H:%M")
endDate_time_obj = datetime.datetime.strptime(endDate_str, "%y-%m-%d %H:%M")
# Unix 타임스탬프를 초 단위로 변환 후 밀리초로 변환
startTime = int(startDate_time_obj.timestamp() * 1000)
endTime = int(endDate_time_obj.timestamp() * 1000)
"""

df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=3000)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df = calculate_values(df)

# 새로운 데이터프레임을 생성
long_rows = []
stop_long_rows = []
short_rows = []
stop_short_rows = []

# 백테스트 실행
for i in range(70, len(df)):
    h_long = ha_long(df, i, 1.4)
    h_short = ha_short(df, i, 1.4)

    s_long = stop_long(df, i)
    s_short = stop_short(df, i)

    if h_long:
        long_rows.append(df.iloc[i])
    if s_long:
        stop_long_rows.append(df.iloc[i])

    if h_short:
        short_rows.append(df.iloc[i])
    if s_short:
        stop_short_rows.append(df.iloc[i])

if long_rows:
    df_long = pd.concat(long_rows, axis=1).T
if stop_long_rows:
    df_stop_long = pd.concat(stop_long_rows, axis=1).T

if short_rows:
    df_short = pd.concat(short_rows, axis=1).T
if stop_short_rows:
    df_stop_short = pd.concat(stop_short_rows, axis=1).T

# 엑셀 파일로 저장
file_path = "backtesting/data/strategy.xlsx"
with pd.ExcelWriter(file_path) as writer:
    df_long.to_excel(writer, sheet_name="h_long", index=False)
    df_stop_long.to_excel(writer, sheet_name="s_long", index=False)
    df_short.to_excel(writer, sheet_name="h_short", index=False)
    df_stop_short.to_excel(writer, sheet_name="s_short", index=False)
