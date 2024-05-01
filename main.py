import logging, datetime, asyncio, math
import Config
from util import (
    setup_logging,
    wait_until_next_interval,
    format_quantity,
)
from market import (
    server_connect,
    fetch_data,
)
from logic import (
    calculate_ema,
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
    cancel_orders,
)


async def main(symbol, leverage, interval):
    logging.info(f"{symbol} {interval} trading program start")
    key = Config.key
    secret = Config.secret
    ratio = Config.ratio
    quantities = []

    while True:
        # 정시(+1초)까지 기다리기
        await wait_until_next_interval(interval=interval)
        logging.info(f"{symbol} {interval} next interval")

        # 해당 심볼 레버리지 변경
        await change_leverage(key, secret, symbol, leverage)

        # 데이터 업데이트
        data = await fetch_data(symbol, interval)

        # 업데이트 후 EMA 계산, RSI 계산 및 추가
        data["EMA10"] = calculate_ema(data, 10)
        data["EMA20"] = calculate_ema(data, 20)
        data["EMA50"] = calculate_ema(data, 50)
        data = calculate_rsi_divergences(data)

        position = await get_position(key, secret, symbol)
        [balance, available] = await get_balance(key, secret)

        # 해당 포지션이 없고 마진이 있는 경우
        if float(position["positionAmt"]) == 0 and (
            balance * (ratio / 100) < available
        ):

            last_row = data.iloc[-1]
            # 추세 롱
            if last_row["EMA10"] > last_row["EMA20"] > last_row["EMA50"] and check_long(
                data
            ):

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = max(last_row["close"], last_row["open"])
                stopPrice = min(last_row["close"], last_row["open"])
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "BUY", quantity, price, "SELL", stopPrice
                )
                logging.info(f"{symbol} {interval} trend long position open")

            # 추세 숏
            elif last_row["EMA10"] < last_row["EMA20"] < last_row[
                "EMA50"
            ] and check_short(data):

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = min(last_row["close"], last_row["open"])
                stopPrice = max(last_row["close"], last_row["open"])
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                logging.info(f"{symbol} {interval} trend short position open")

            # 역추세 롱
            elif last_row["bullish"]:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = max(last_row["close"], last_row["open"])
                stopPrice = min(last_row["close"], last_row["open"])
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "BUY", quantity, price, "SELL", stopPrice
                )
                logging.info(f"{symbol} {interval} reverse long position open")

            # 역추세 숏
            elif last_row["bearish"]:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = min(last_row["close"], last_row["open"])
                stopPrice = max(last_row["close"], last_row["open"])
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                logging.info(f"{symbol} {interval} reverse short position open")

        # 해당 포지션이 있는 경우, 매 시간마다 1/3씩 포지션 종료
        elif float(position["positionAmt"]) > 0:

            if not quantities:
                divide = float(position["positionAmt"]) / 3
                value = format_quantity(divide, symbol)
                remainder = float(position["positionAmt"]) - 2 * value
                quantities.append(value)
                quantities.append(remainder)
                quantities.append(value)

            await tp_sl(key, secret, symbol, "SELL", quantities[0])
            logging.info(f"{symbol} {interval} long position close {quantities[0]}")
            quantities.pop(0)

        elif float(position["positionAmt"]) < 0:

            if not quantities:
                divide = float(position["positionAmt"]) / 3
                value = format_quantity(divide, symbol)
                remainder = float(position["positionAmt"]) - 2 * value
                quantities.append(value)
                quantities.append(remainder)
                quantities.append(value)

            await tp_sl(key, secret, symbol, "BUY", quantities[0])
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
