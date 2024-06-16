import asyncio
import pandas as pd
import logging
import datetime
from functools import partial
from binance.um_futures import UMFutures
from binance.error import ClientError


# 서버 연결 테스트
def server_connect() -> bool:
    um_futures_client = UMFutures()
    response = um_futures_client.ping()

    if not response:
        return True
    else:
        return False


# 과거 700개 데이터 불러오기
async def fetch_data(symbol, interval) -> pd.DataFrame:
    loop = asyncio.get_running_loop()
    client = UMFutures()
    func = partial(
        client.klines,
        symbol=symbol,
        interval=interval,
        limit=700,
    )
    try:
        bars = await loop.run_in_executor(None, func)
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
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
            axis=1,
            inplace=True,
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
