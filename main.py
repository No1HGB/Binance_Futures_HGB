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
    calculate_values,
    is_divergence,
    cal_stop_price,
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
        # 정시(+2초)까지 기다리기
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
        data = calculate_values(data)

        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])

        [balance, available] = await get_balance(key, secret)
        [bullish, bearish] = is_divergence(data)
        last_row = data.iloc[-1]
        volume = last_row["volume"]
        if symbol == "BTCUSDT":
            volume_MA = last_row["volume_MA"] * 1.1
        else:
            volume_MA = last_row["volume_MA"]

        # 해당 포지션이 없고 마진이 있는 경우
        if positionAmt == 0 and (balance * (ratio / 100) < available):

            # 추세 롱
            if last_row["EMA10"] > last_row["EMA20"] > last_row["EMA50"] and check_long(
                data
            ):

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                stopPrice = cal_stop_price(last_row, "BUY", symbol)
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

                price = last_row["close"]
                stopPrice = cal_stop_price(last_row, "SELL", symbol)
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                logging.info(f"{symbol} {interval} trend short position open")

            # 역추세 롱
            elif bullish:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                stopPrice = cal_stop_price(last_row, "BUY", symbol)
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "BUY", quantity, price, "SELL", stopPrice
                )
                logging.info(f"{symbol} {interval} reverse long position open")

            # 역추세 숏
            elif bearish:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                stopPrice = cal_stop_price(last_row, "SELL", symbol)
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                logging.info(f"{symbol} {interval} reverse short position open")

        # 해당 포지션이 있는 경우, 일부 포지션 종료
        elif positionAmt > 0:

            # quantity 담는 로직
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                divide = positionAmt / 2
                value = format_quantity(divide, symbol)
                remainder = positionAmt - value
                remainder = format_quantity(remainder, symbol)
                quantities.append(value)
                quantities.append(remainder)
                logging.info(f"value:{value} / remainder:{remainder}")

            if quantities[0] > 0 and volume >= volume_MA:
                await tp_sl(key, secret, symbol, "SELL", quantities[0])
                quantities.pop(0)
                logging.info(f"{symbol} {interval} long position close {quantities[0]}")

        elif positionAmt < 0:

            # quantity 담는 로직
            positionAmt = -positionAmt
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                divide = positionAmt / 2
                value = format_quantity(divide, symbol)
                remainder = positionAmt - value
                remainder = format_quantity(remainder, symbol)
                quantities.append(value)
                quantities.append(remainder)
                logging.info(f"value:{value} / remainder:{remainder}")

            if quantities[0] > 0 and volume >= volume_MA:
                await tp_sl(key, secret, symbol, "BUY", quantities[0])
                quantities.pop(0)
                logging.info(
                    f"{symbol} {interval} short position close {quantities[0]}"
                )


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
