import datetime, math, time
import pandas as pd
import logging
import pytz
from binance.um_futures import UMFutures
from binance.error import ClientError


def wait_until_next_interval():
    now = datetime.datetime.now(datetime.UTC)

    next_time = (
        now.replace(second=0, microsecond=0)
        + datetime.timedelta(minutes=1)
        + datetime.timedelta(seconds=1)
    )

    wait_seconds = (next_time - now).total_seconds()
    time.sleep(wait_seconds)


def fetch_data(symbol, interval) -> pd.DataFrame:

    client = UMFutures()
    try:
        bars = client.klines(symbol=symbol, interval=interval, limit=800)
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
        # 만약 현재 시간 봉 데이터가 존재하면 마지막 행 제거
        now = datetime.datetime.now(datetime.UTC)
        open_time = int(
            now.replace(minute=0, second=0, microsecond=0).timestamp() * 1000
        )
        if df.iloc[-1]["open_time"] == open_time:
            df.drop(df.index[-1], inplace=True)

        # 모든 열을 숫자형으로 변환
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        return df

    except ClientError as error:
        logging.error(
            f"Found error. status(fetch_data){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(fetch_data){symbol}: {error}")


def open_position(key, secret, symbol, side, quantity, price, stopSide, stopPrice):
    now_timestamp = datetime.datetime.now(datetime.UTC).timestamp() * 1000
    timestamp = now_timestamp + (59 * 60 * 1000)
    timestamp = math.floor(timestamp)

    um_futures_client = UMFutures(key=key, secret=secret)

    try:
        um_futures_client.new_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            timeInForce="GTD",
            goodTillDate=timestamp,
            price=price,
        )
        # 손절로직
        um_futures_client.new_order(
            symbol=symbol,
            side=stopSide,
            type="STOP_MARKET",
            stopPrice=stopPrice,
            closePosition="true",
        )

    except ClientError as error:
        logging.error(
            f"Found error. status(open_position){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(open_position){symbol}: {error}")


def cancel_orders(key, secret, symbol):

    um_futures_client = UMFutures(key=key, secret=secret)

    try:
        um_futures_client.cancel_open_orders(symbol=symbol, recvWindow=1000)

    except ClientError as error:
        logging.error(
            f"Found error. status(cancel_orders){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(cancel_orders){symbol}: {error}")


def convert_unix_to_kst(unix_timestamp):
    unix_timestamp = unix_timestamp / 1000
    # UTC 기준 datetime 객체 생성
    utc_time = datetime.datetime.fromtimestamp(unix_timestamp)

    # pytz를 사용하여 UTC 시간대 정보 추가
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # 한국 시간대로 변환
    kst_time = utc_time.astimezone(pytz.timezone("Asia/Seoul"))

    return utc_time


# 추세 롱
def trend_long(data: pd.DataFrame, symbol) -> bool:
    last_oct = data.tail(8)
    volume = data.iloc[-1]["volume"]
    volume_MA = data.iloc[-1]["volume_MA"]
    if symbol == "BTCUSDT":
        rsi_down = 30
        rsi_up = 70
    else:
        rsi_down = 33
        rsi_up = 73

    if (
        last_oct.iloc[-1]["close"] > last_oct.iloc[-1]["open"]
        and last_oct.iloc[-1]["open"] > last_oct.iloc[-1]["EMA50"]
    ):
        pre_max_value = last_oct["up"][:-1].max()

        return (
            last_oct.iloc[-1]["close"] > pre_max_value
            and volume >= volume_MA * 1.5
            and last_oct.iloc[-1]["rsi"] > rsi_down
            and last_oct.iloc[-1]["rsi"] < rsi_up
        )

    return False


def trend(df: pd.DataFrame):
    df["trend_long"] = False

    # 조건에 따라 "trend_long" 값 설정
    for i in range(7, len(df)):
        if df.loc[i, "close"] > df.loc[i - 7, "up"]:
            df.loc[i, "trend_long"] = True


# 추세 숏
def trend_short(data: pd.DataFrame, symbol) -> bool:
    last_oct = data.tail(8)
    volume = data.iloc[-1]["volume"]
    volume_MA = data.iloc[-1]["volume_MA"]
    if symbol == "BTCUSDT":
        rsi_down = 30
        rsi_up = 70
        volume_coeff = 1.5
    else:
        rsi_down = 33
        rsi_up = 73
        volume_coeff = 1.2

    if (
        last_oct.iloc[-1]["close"] < last_oct.iloc[-1]["open"]
        and last_oct.iloc[-1]["open"] < last_oct.iloc[-1]["EMA50"]
    ):
        pre_min_value = last_oct["down"][:-1].min()

        return (
            last_oct.iloc[-1]["close"] < pre_min_value
            and volume >= volume_MA * volume_coeff
            and last_oct.iloc[-1]["rsi"] > rsi_down
            and last_oct.iloc[-1]["rsi"] < rsi_up
        )

    return False


now = datetime.datetime.now(datetime.UTC)
end_datetime = (
    now.replace(minute=0, second=0, microsecond=0)
    + datetime.timedelta(hours=1)
    + datetime.timedelta(milliseconds=100)
)
endTime = int(end_datetime.timestamp() * 1000)


client = UMFutures()

bars = client.klines(symbol="BTCUSDT", interval="1h", limit=800)
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

"""
# 만약 현재 시간 봉 데이터가 존재하면 마지막 행 제거
now = datetime.datetime.now(datetime.UTC)
open_time = int(now.replace(minute=0, second=0, microsecond=0).timestamp() * 1000)
if df.iloc[-1]["open_time"] == open_time:
    df.drop(df.index[-1], inplace=True)
"""
print(df.iloc[-1])
