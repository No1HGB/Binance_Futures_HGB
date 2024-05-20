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
    divergence,
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
    position_cnt = 0

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

        last_row = data.iloc[-1]
        volume = last_row["volume"]
        volume_MA = last_row["volume_MA"]

        [div_long, div_short] = divergence(data)
        rev_long = reverse_long(data)
        rev_short = reverse_short(data)
        tre_long = trend_long(data, symbol)
        tre_short = trend_short(data, symbol)

        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])

        # rsi 손익 기준선
        if symbol == "BTCUSDT":
            rsi_up = 70
            rsi_down = 30
        else:
            rsi_up = 73
            rsi_down = 33

        # 해당 포지션이 있는 경우, 포지션 종료 로직
        if positionAmt > 0:
            position_cnt += 1
            logging.info(f"position count:{position_cnt}")

            # quantity 담는 로직
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                if symbol == "BTCUSDT":
                    divide = positionAmt / 3
                else:
                    divide = positionAmt / 2
                value = format_quantity(divide, symbol)
                if symbol == "BTCUSDT":
                    remainder = positionAmt - 2 * value
                else:
                    remainder = positionAmt - value
                remainder = format_quantity(remainder, symbol)
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                    if symbol == "BTCUSDT":
                        quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if tre_long or rev_long or div_long:
                    position_cnt = 0
                    logging.info(
                        f"position count init, tre_long:{tre_long}, rev_long:{rev_long},div_long:{div_long}"
                    )

                if tre_short or rev_short or div_short or position_cnt >= 12:
                    await tp_sl(key, secret, symbol, "SELL", positionAmt)
                    logging.info(
                        f"{symbol} {interval} long position all close {positionAmt}"
                    )
                    quantities = []
                    position_cnt = 0

                elif volume >= volume_MA * 1.5 or last_row["rsi"] >= rsi_up:
                    await tp_sl(key, secret, symbol, "SELL", quantities[0])
                    logging.info(
                        f"{symbol} {interval} long position close {quantities[0]}"
                    )
                    quantities.pop(0)
                    if not quantities:
                        position_cnt = 0
                        logging.info("position count init")

        elif positionAmt < 0:
            position_cnt += 1
            logging.info(f"position count:{position_cnt}")

            # quantity 담는 로직
            positionAmt = -positionAmt
            if not quantities:
                if symbol == "SOLUSDT":
                    positionAmt = int(positionAmt)
                if symbol == "BTCUSDT":
                    divide = positionAmt / 3
                else:
                    divide = positionAmt / 2
                value = format_quantity(divide, symbol)
                if symbol == "BTCUSDT":
                    remainder = positionAmt - 2 * value
                else:
                    remainder = positionAmt - value
                remainder = format_quantity(remainder, symbol)
                if remainder > 0:
                    quantities.append(remainder)
                if value > 0:
                    quantities.append(value)
                    if symbol == "BTCUSDT":
                        quantities.append(value)
                logging.info(f"remainder:{remainder} / value:{value}")

            if quantities[0] > 0:
                if tre_short or rev_short or div_short:
                    position_cnt = 0
                    logging.info(
                        f"position count init, tre_short:{tre_short}, rev_short:{rev_short},div_short:{div_short}"
                    )

                if tre_long or rev_long or div_long or position_cnt >= 12:
                    await tp_sl(key, secret, symbol, "BUY", positionAmt)
                    logging.info(
                        f"{symbol} {interval} short position all close {positionAmt}"
                    )
                    quantities = []
                    position_cnt = 0

                elif volume >= volume_MA * 1.5 or last_row["rsi"] <= rsi_down:
                    await tp_sl(key, secret, symbol, "BUY", quantities[0])
                    logging.info(
                        f"{symbol} {interval} short position close {quantities[0]}"
                    )
                    quantities.pop(0)
                    if not quantities:
                        position_cnt = 0
                        logging.info("position count init")

        # 포지션이 종료된 경우가 있기 때문에 다시 가져오기
        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])
        [balance, available] = await get_balance(key, secret)

        # 해당 포지션이 없고 마진이 있는 경우
        if positionAmt == 0 and (balance * (ratio / 100) < available):

            # 롱
            if rev_long or tre_long or div_long:

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

                position_cnt = 0

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} long position open. tre_long:{tre_long}, rev_long:{rev_long}, div_long:{div_long}"
                )

            # 숏
            elif rev_short or tre_short or div_short:

                await cancel_orders(key, secret, symbol)
                logging.info(f"{symbol} open orders cancel")

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                amount = price * quantity
                profitPrice = cal_profit_price(price, "SELL", symbol, amount, balance)
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

                position_cnt = 0

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} short position open. tre_short:{tre_short}, rev_short:{rev_short}, div_short:{div_short}"
                )


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
