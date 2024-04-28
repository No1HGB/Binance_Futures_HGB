import pandas as pd
from binance.um_futures import UMFutures


# 서버 연결 테스트
def server_connect() -> bool:
    um_futures_client = UMFutures()
    response = um_futures_client.ping()

    if not response:
        return True
    else:
        return False


# 과거 1500개 데이터 불러오기
def fetch_historical_data(symbol, interval, endTime) -> pd.DataFrame:
    client = UMFutures()
    bars = client.klines(symbol=symbol, interval=interval, endTime=endTime, limit=721)
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
    # 인덱스 설정
    df.set_index("open_time", inplace=True)
    return df


# 최신 버전으로 데이터 업데이트
def update_data(symbol, interval, endTime, data: pd.DataFrame) -> pd.DataFrame:
    client = UMFutures()
    latest_data = client.klines(
        symbol=symbol, interval=interval, endTime=endTime, limit=1
    )
    latest_point = latest_data[-1]
    new_row = pd.DataFrame(
        [
            {
                "open_time": latest_point[0],
                "open": latest_point[1],
                "high": latest_point[2],
                "low": latest_point[3],
                "close": latest_point[4],
                "volume": latest_point[5],
                "close_time": latest_point[6],
                "quote_asset_volume": latest_point[7],
                "number_of_trades": latest_point[8],
                "taker_buy_base_asset_volume": latest_point[9],
                "taker_buy_quote_asset_volume": latest_point[10],
                "ignore": latest_point[11],
            }
        ]
    )
    # 모든 열을 숫자형으로 변환
    new_row = new_row.apply(pd.to_numeric, errors="coerce")
    new_row.set_index("open_time", inplace=True)

    # 가장 오래된 행 제거 및 새 행 추가: 가장 오래된 데이터 제거 및 현재 데이터 추가
    data = pd.concat([data.iloc[1:], new_row])
    return data
