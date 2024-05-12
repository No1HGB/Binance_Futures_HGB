import logging, asyncio
from enum import Enum, auto
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


class State(Enum):
    NONE = auto()
    TREND_LONG = auto()
    TREND_SHORT = auto()
    REVERSE_LONG = auto()
    REVERSE_SHORT = auto()


async def main(symbol, leverage, interval):
    logging.info(f"{symbol} {interval} trading program start")
    key = Config.key
    secret = Config.secret
    ratio = Config.ratio
    quantities = []
    state = State.NONE

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

        trend_long = last_row["EMA10"] > last_row["EMA20"] > last_row[
            "EMA50"
        ] and check_long(data)

        trend_short = last_row["EMA10"] < last_row["EMA20"] < last_row[
            "EMA50"
        ] and check_short(data)

        # 해당 포지션이 없고 마진이 있는 경우
        if positionAmt == 0 and (balance * (ratio / 100) < available):

            # 추세 롱
            if trend_long:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "BUY", symbol, amount, balance)

                await open_position(
                    key, secret, symbol, "BUY", quantity, price, "SELL", stopPrice
                )
                state = State.TREND_LONG
                logging.info(f"{symbol} {interval} trend long position open")

            # 추세 숏
            elif trend_short:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "SELL", symbol, amount, balance)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                state = State.TREND_SHORT
                logging.info(f"{symbol} {interval} trend short position open")

            # 역추세 롱
            elif bullish:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "BUY", symbol, amount, balance)

                await open_position(
                    key, secret, symbol, "BUY", quantity, price, "SELL", stopPrice
                )
                state = State.REVERSE_LONG
                logging.info(f"{symbol} {interval} reverse long position open")

            # 역추세 숏
            elif bearish:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "SELL", symbol, amount, balance)

                await open_position(
                    key, secret, symbol, "SELL", quantity, price, "BUY", stopPrice
                )
                state = State.REVERSE_SHORT
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
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if (
                    volume >= volume_MA
                    or (state == State.TREND_LONG and bearish)
                    or (state == State.REVERSE_LONG and trend_short)
                ):
                    price = last_row["close"]
                    await tp_sl(key, secret, symbol, "SELL", quantities[0], price)
                    logging.info(
                        f"{symbol} {interval} long position close {quantities[0]}"
                    )
                    quantities.pop(0)
                    if not quantities:
                        await cancel_orders(key, secret, symbol)
                        state = State.NONE

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
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if (
                    volume >= volume_MA
                    or (state == State.TREND_SHORT and bullish)
                    or (state == State.REVERSE_SHORT and trend_long)
                ):
                    price = last_row["close"]
                    await tp_sl(key, secret, symbol, "BUY", quantities[0], price)
                    logging.info(
                        f"{symbol} {interval} short position close {quantities[0]}"
                    )
                    quantities.pop(0)
                    if not quantities:
                        await cancel_orders(key, secret, symbol)
                        state = State.NONE


symbols = Config.symbols
leverages = Config.leverages
interval = Config.interval


async def run_multiple_tasks():
    # 여러 매개변수로 main 함수를 비동기적으로 실행
    await asyncio.gather(
        main(symbols[0], leverages[0], interval),
        main(symbols[1], leverages[1], interval),
    )


if server_connect():
    setup_logging()
    asyncio.run(run_multiple_tasks())
else:
    print("server connect problem")
