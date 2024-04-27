import logging, datetime, asyncio
import Config
from util import (
    setup_logging,
    rounded_time,
    wait_until_next_interval,
    divide_and_format,
)
from market import (
    server_connect,
    fetch_historical_data,
    update_data,
)
from logic import (
    calculate_ema,
    check_box,
    check_long,
    check_short,
    calculate_rsi_divergences,
)
from account import (
    get_position,
    get_balance,
    change_leverage,
    open_position,
    tp_sl,
)


async def main(symbol, leverage, interval):
    logging.info(f"{symbol} {interval} trading program start")
    key = Config.key
    secret = Config.secret
    quantities = []

    # 현재 UTC 시간
    current_utc_time = datetime.datetime.now(datetime.UTC)
    rounded_current_utc_time = rounded_time(current_utc_time, interval)

    # 시작 시간과 끝 시간의 Unix 타임스탬프를 밀리초 단위로 계산
    end_timestamp = int(rounded_current_utc_time.timestamp() * 1000)

    # 과거 1500개의 데이터 가져오기
    data = fetch_historical_data(symbol, interval, endTime=end_timestamp)

    # 해당 심볼 레버리지 변경
    # change_leverage(key, secret, symbol, leverage)

    while True:
        # 정시까지 기다리기
        await wait_until_next_interval(interval=interval)
        logging.info(f"{symbol} {interval} next interval")
        # 현재 시간으로 업데이트
        current_utc_time = datetime.datetime.now(datetime.UTC)
        rounded_current_utc_time = rounded_time(current_utc_time, interval)
        end_timestamp = int(rounded_current_utc_time.timestamp() * 1000)

        # 데이터 업데이트 전 4개 봉 박스권 확인
        is_box = check_box(data, symbol, interval)

        # 1봉 데이터 업데이트
        data = update_data(
            symbol=symbol, interval=interval, endTime=end_timestamp, data=data
        )

        # 업데이트 후 EMA 계산, RSI 계산 및 추가
        data["EMA10"] = calculate_ema(data, 10)
        data["EMA20"] = calculate_ema(data, 20)
        data["EMA50"] = calculate_ema(data, 50)
        data = calculate_rsi_divergences(data)

        position = get_position(key, secret, symbol)
        balances = get_balance(key, secret)

        # 해당 포지션이 없는 경우
        if float(position["positionAmt"]) == 0:

            # 추세 트레이딩 실행 로직
            last_row = data.iloc[-1]
            if (
                last_row["EMA10"] > last_row["EMA20"] > last_row["EMA50"]
                and is_box
                and check_long(data, symbol, interval)
            ):
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "BUY",
                    balances[0],
                    last_row["close"],
                )
                # 손절가 지정
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "SELL",
                    balances[0],
                    last_row["open"],
                )
                logging.info(f"{symbol} {interval} trend long position open")

            elif (
                last_row["EMA10"] < last_row["EMA20"] < last_row["EMA50"]
                and is_box
                and check_short(data, symbol, interval)
            ):
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "SELL",
                    balances[0],
                    last_row["close"],
                )
                # 손절가 지정
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "BUY",
                    balances[0],
                    last_row["open"],
                )
                logging.info(f"{symbol} {interval} trend short position open")

            # 역추세(추세반전) 트레이딩 실행 로직
            elif last_row["bullish"]:
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "BUY",
                    balances[0],
                    last_row["close"],
                )
                # 손절가 지정
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "SELL",
                    balances[0],
                    last_row["open"],
                )
                logging.info(f"{symbol} {interval} reverse long position open")
            elif last_row["bearish"]:
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "SELL",
                    balances[0],
                    last_row["close"],
                )
                # 손절가 지정
                open_position(
                    key,
                    secret,
                    symbol,
                    leverage,
                    "BUY",
                    balances[0],
                    last_row["open"],
                )
                logging.info(f"{symbol} {interval} reverse short position open")

        # 해당 포지션이 있는 경우, 1/3씩 포지션 종료
        elif float(position["positionAmt"]) > 0:
            if not quantities:
                value = divide_and_format(float(position["positionAmt"]))
                remainder = float(position["positionAmt"]) - 2 * value
                quantities.append(value)
                quantities.append(remainder)
                quantities.append(value)
            tp_sl(key, secret, symbol, "SELL", quantities[0])
            logging.info(f"{symbol} {interval} long position close {quantities[0]}")
            quantities.pop(0)

        elif float(position["positionAmt"]) < 0:
            if not quantities:
                value = divide_and_format(float(position["positionAmt"]))
                remainder = float(position["positionAmt"]) - 2 * value
                quantities.append(value)
                quantities.append(remainder)
                quantities.append(value)
            tp_sl(key, secret, symbol, "BUY", quantities[0])
            logging.info(f"{symbol} {interval} short position close {quantities[0]}")
            quantities.pop(0)


symbols = Config.symbols
leverages = Config.leverages
interval = Config.interval


async def run_multiple_tasks():
    # 여러 매개변수로 main 함수를 비동기적으로 실행
    await asyncio.gather(
        main(symbols[0], leverages[0], interval),
        main(symbols[1], leverages[1], interval),
        main(symbols[2], leverages[2], interval),
    )


if server_connect():
    setup_logging()
    asyncio.run(run_multiple_tasks())
else:
    print("server connect problem")
