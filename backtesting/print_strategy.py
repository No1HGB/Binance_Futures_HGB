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


def fetch_data(symbol, interval, numbers):
    client = UMFutures()
    bars = client.klines(
        symbol=symbol,
        interval=interval,
        limit=numbers,
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


"""
startDate_str = input()
endDate_str = input()
startDate_time_obj = datetime.datetime.strptime(startDate_str, "%y-%m-%d %H:%M")
endDate_time_obj = datetime.datetime.strptime(endDate_str, "%y-%m-%d %H:%M")
# Unix 타임스탬프를 초 단위로 변환 후 밀리초로 변환
startTime = int(startDate_time_obj.timestamp() * 1000)
endTime = int(endDate_time_obj.timestamp() * 1000)
"""

df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=1000)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df = calculate_values(df)

# 새로운 데이터프레임을 생성
long_rows = []
short_rows = []


# 백테스트 실행
for i in range(70, len(df)):
    m_long = maker_long(df, i, 1.5)
    m_short = maker_short(df, i, 1.5)

    if m_long:
        long_rows.append(df.iloc[i])

    if m_short:
        short_rows.append(df.iloc[i])

if long_rows:
    df_long = pd.concat(long_rows, axis=1).T

if short_rows:
    df_short = pd.concat(short_rows, axis=1).T

# 엑셀 파일로 저장
file_path = "backtesting/data/strategy.xlsx"
with pd.ExcelWriter(file_path) as writer:
    df_long.to_excel(writer, sheet_name="m_long", index=False)
    df_short.to_excel(writer, sheet_name="m_short", index=False)
