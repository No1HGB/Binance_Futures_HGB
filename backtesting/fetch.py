import pandas as pd
import datetime
from binance.um_futures import UMFutures


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

    # 모든 열을 숫자형으로 변환
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

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
