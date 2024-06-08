import logging, asyncio
import Config
from util import (
    setup_logging,
    wait_until_next_interval,
    format_quantity,
)
from calculation import (
    calculate_ema,
    calculate_values,
)
from market import (
    server_connect,
    fetch_data,
)
from logic import (
    cal_stop_price,
    cal_profit_price,
    trend_long,
    trend_short,
    reverse_long,
    reverse_short,
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
    start = 0

    while True:
        # 정시(+2초)까지 기다리기
        await wait_until_next_interval(interval=interval)
        logging.info(f"{symbol} {interval} next interval")

        # 해당 심볼 레버리지 변경
        if start == 0:
            await change_leverage(key, secret, symbol, leverage)
            start += 1

        # 데이터 업데이트
        data = await fetch_data(symbol, interval)

        # 업데이트 후 EMA 계산, RSI 계산 및 추가
        data["EMA50"] = calculate_ema(data, 50)
        data = calculate_values(data)

        last_row = data.iloc[-1]

        t_long = trend_long(data)
        t_short = trend_short(data)
        r_long = reverse_long(data)
        r_short = reverse_short(data)

        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])

        # 해당 포지션이 있는 경우, 포지션 종료 로직
        if positionAmt > 0:

            if t_short or r_short:
                await tp_sl(key, secret, symbol, "SELL", positionAmt)
                logging.info(f"{symbol} {interval} long position all close")

        elif positionAmt < 0:
            positionAmt = abs(positionAmt)

            if t_long or r_long:
                await tp_sl(key, secret, symbol, "BUY", positionAmt)
                logging.info(f"{symbol} {interval} short position all close")

        # 포지션 다시 가져오기(종료된 경우 고려)
        position = await get_position(key, secret, symbol)
        positionAmt = float(position["positionAmt"])
        [balance, available] = await get_balance(key, secret)

        # 해당 포지션이 없고 마진이 있는 경우 포지션 진입
        if positionAmt == 0 and (balance * (ratio / 100) < available):

            await cancel_orders(key, secret, symbol)
            logging.info(f"{symbol} open orders cancel")

            # 롱
            if t_long or r_long:

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                stopPrice = cal_stop_price(price, "BUY", symbol)
                profitPrice = cal_profit_price(price, "BUY", symbol)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "BUY",
                    quantity,
                    "SELL",
                    stopPrice,
                    profitPrice,
                )

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} long position open. t:{t_long}, r:{r_long}"
                )

            # 숏
            elif t_short or r_short:

                price = last_row["close"]
                raw_quantity = balance * (ratio / 100) / price * leverage
                quantity = format_quantity(raw_quantity, symbol)
                stopPrice = cal_stop_price(price, "SELL", symbol)
                profitPrice = cal_profit_price(price, "SELL", symbol)

                await open_position(
                    key,
                    secret,
                    symbol,
                    "SELL",
                    quantity,
                    "BUY",
                    stopPrice,
                    profitPrice,
                )

                # 로그 기록
                logging.info(
                    f"{symbol} {interval} short position open. t:{t_short}, r:{r_short}"
                )


symbols = Config.symbols
leverage = Config.leverage
interval = Config.interval


async def run_multiple_tasks():
    # 여러 매개변수로 main 함수를 비동기적으로 실행
    await asyncio.gather(
        main(symbols[0], leverage, interval),
        main(symbols[1], leverage, interval),
    )


if server_connect():
    setup_logging()
    asyncio.run(run_multiple_tasks())
else:
    print("server connect problem")
