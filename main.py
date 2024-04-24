import datetime


import Config
from util import (
    rounded_time,
    wait_until_next_interval,
)
from market import (
    fetch_historical_data,
    update_data,
)
from logic import (
    calculate_ema,
    check_box,
    check_long,
    check_short,
)


def main():
    """
    실행 전 서버 연결 및 서버 시간과 차이 체크, 서버 통신 함수들 None 리턴 여부 확인
    """

    key = Config.key
    secret = Config.secret
    symbol = Config.symbol
    interval = Config.interval

    # 현재 UTC 시간
    current_utc_time = datetime.datetime.now(datetime.UTC)
    rounded_current_utc_time = rounded_time(current_utc_time, interval)

    # 시작 시간과 끝 시간의 Unix 타임스탬프를 밀리초 단위로 계산
    end_timestamp = int(rounded_current_utc_time.timestamp() * 1000)

    # 과거 1500개의 데이터 가져오기
    data = fetch_historical_data(symbol, interval, endTime=end_timestamp)

    # 매 시간마다 반복
    while True:
        wait_until_next_interval(interval=interval)
        current_utc_time = datetime.datetime.now(datetime.UTC)
        rounded_current_utc_time = rounded_time(current_utc_time, interval)
        end_timestamp = int(rounded_current_utc_time.timestamp() * 1000)

        # 데이터 업데이트 전 4개 봉 박스권 확인
        is_box = check_box(data, interval)

        # 1봉 데이터 업데이트
        data = update_data(
            symbol=symbol, interval=interval, endTime=end_timestamp, data=data
        )
        # EMA 계산
        data["EMA10"] = calculate_ema(data, 10)
        data["EMA20"] = calculate_ema(data, 20)
        data["EMA50"] = calculate_ema(data, 50)

        # 트레이딩 실행 로직
        last_row = data.iloc[-1]
        if (
            last_row["EMA10"] > last_row["EMA20"] > last_row["EMA50"]
            and is_box
            and check_long(data, interval)
        ):
            print("Consider long position")
        elif (
            last_row["EMA10"] < last_row["EMA20"] < last_row["EMA50"]
            and is_box
            and check_short(data, interval)
        ):
            print("Consider short position")
        else:
            pass


if __name__ == "__main__":
    main()
