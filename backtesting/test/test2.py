import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pandas as pd
import datetime
from binance.um_futures import UMFutures
from calculate import calculate_ema, calculate_values, cal_resistance
from openpyxl import load_workbook


def fetch_one_data(symbol, interval, startTime, endTime):
    client = UMFutures()
    bars = client.klines(
        symbol=symbol,
        interval=interval,
        startTime=startTime,
        endTime=endTime,
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


startDate_str = input()
endDate_str = input()
startDate_time_obj = datetime.datetime.strptime(startDate_str, "%y-%m-%d %H:%M")
endDate_time_obj = datetime.datetime.strptime(endDate_str, "%y-%m-%d %H:%M")
# Unix 타임스탬프를 초 단위로 변환 후 밀리초로 변환
startTime = int(startDate_time_obj.timestamp() * 1000)
endTime = int(endDate_time_obj.timestamp() * 1000)

df: pd.DataFrame = fetch_one_data(
    symbol="BTCUSDT", interval="1h", startTime=startTime, endTime=endTime
)
df = calculate_values(df)

resistance = cal_resistance(df)
print(resistance)

"""
output_file = "backtesting/data/output.xlsx"
df.to_excel(output_file, index=False)
"""
