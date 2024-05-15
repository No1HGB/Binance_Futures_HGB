import logging, asyncio
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
    calculate_values,
    cal_profit_price,
    cal_stop_price,
    reverse_long,
    reverse_short,
    trend_long,
    trend_short,
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
        data["EMA50"] = calculate_ema(data, 50)
        data = calculate_values(data)

        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])

        [balance, available] = await get_balance(key, secret)

        last_row = data.iloc[-1]
        volume = last_row["volume"]
        volume_MA = last_row["volume_MA"]

        rev_long = reverse_long(data)
        rev_short = reverse_short(data)
        tre_long = trend_long(data)
        tre_short = trend_short(data)

        # 해당 포지션이 있는 경우, 포지션 종료 로직
        if positionAmt > 0:

            # quantity 담는 로직
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                divide = positionAmt / 3
                value = format_quantity(divide, symbol)
                remainder = positionAmt - 2 * value
                remainder = format_quantity(remainder, symbol)
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                    quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if tre_short or rev_short:
                    await tp_sl(key, secret, symbol, "SELL", positionAmt)
                    logging.info(
                        f"{symbol} {interval} long position all close {positionAmt}"
                    )
                    quantities = []

                elif volume >= volume_MA * 1.5 or last_row["rsi"] >= 70:
                    await tp_sl(key, secret, symbol, "SELL", quantities[0])
                    logging.info(
                        f"{symbol} {interval} long position close {quantities[0]}"
                    )
                    quantities.pop(0)

        elif positionAmt < 0:

            # quantity 담는 로직
            positionAmt = -positionAmt
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                divide = positionAmt / 3
                value = format_quantity(divide, symbol)
                remainder = positionAmt - 2 * value
                remainder = format_quantity(remainder, symbol)
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                    quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if tre_long or rev_long:
                    await tp_sl(key, secret, symbol, "BUY", positionAmt)
                    logging.info(
                        f"{symbol} {interval} short position all close {positionAmt}"
                    )
                    quantities = []

                elif volume >= volume_MA * 1.5 or last_row["rsi"] <= 30:
                    await tp_sl(key, secret, symbol, "BUY", quantities[0])
                    logging.info(
                        f"{symbol} {interval} short position close {quantities[0]}"
                    )
                    quantities.pop(0)

        # 해당 포지션이 없고 마진이 있는 경우
        if positionAmt == 0 and (balance * (ratio / 100) < available):

            # 역추세 롱
            if rev_long:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                profitPrice = cal_profit_price(price, "BUY", symbol, amount, balance)
                stopPrice = cal_stop_price(price, "BUY", symbol, amount, balance)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "BUY",
                    quantity,
                    price,
                    "SELL",
                    profitPrice,
                    stopPrice,
                )
                logging.info(f"{symbol} {interval} reverse long position open")

            # 역추세 숏
            elif rev_short:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "SELL", symbol, amount, balance)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "SELL",
                    quantity,
                    price,
                    "BUY",
                    profitPrice,
                    stopPrice,
                )
                logging.info(f"{symbol} {interval} reverse short position open")

            # 추세 롱
            elif tre_long:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "BUY", symbol, amount, balance)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "BUY",
                    quantity,
                    price,
                    "SELL",
                    profitPrice,
                    stopPrice,
                )
                logging.info(f"{symbol} {interval} trend long position open")

            # 추세 숏
            elif tre_short:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                stopPrice = cal_stop_price(price, "SELL", symbol, amount, balance)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "SELL",
                    quantity,
                    price,
                    "BUY",
                    profitPrice,
                    stopPrice,
                )
                logging.info(f"{symbol} {interval} trend short position open")


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
