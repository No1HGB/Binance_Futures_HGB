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
    cal_stop_price,
    just_long,
    just_short,
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
    short_cnt = 0

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

        [div_long, div_short] = divergence(data)
        long = just_long(data, symbol)
        short = just_short(data, symbol)

        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])
        [balance, available] = await get_balance(key, secret)

        # 해당 포지션이 있는 경우, 포지션 종료 로직
        if positionAmt > 0:
            if short or div_short:
                await tp_sl(key, secret, symbol, "SELL", positionAmt)
                logging.info(f"{symbol} {interval} long position all close")

            elif last_row["close"] < last_row["open"]:
                await tp_sl(key, secret, symbol, "SELL", positionAmt)
                logging.info(f"{symbol} {interval} long position close {positionAmt}")

        elif positionAmt < 0:
            positionAmt = abs(positionAmt)

            if last_row["close"] > last_row["open"]:
                short_cnt += 1

            if long or div_long:
                await tp_sl(key, secret, symbol, "BUY", positionAmt)
                logging.info(f"{symbol} {interval} short position all close")

            elif short_cnt >= 3:
                await tp_sl(key, secret, symbol, "BUY", positionAmt)
                logging.info(f"{symbol} {interval} short position close {positionAmt}")

        # 해당 포지션이 없고 마진이 있는 경우 포지션 진입
        elif positionAmt == 0 and (balance * (ratio / 100) < available):

            short_cnt = 0

            # 롱
            if long or div_long:

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
                    "SELL",
                    stopPrice,
                )

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} long position open. div_long:{div_long}"
                )

            # 숏
            elif short or div_short:
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
                    "BUY",
                    stopPrice,
                )

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} short position open. div_short:{div_short}"
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
