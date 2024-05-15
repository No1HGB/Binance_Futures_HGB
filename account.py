import logging, datetime, math, asyncio
from binance.um_futures import UMFutures
from binance.error import ClientError
from functools import partial


async def get_position(key, secret, symbol):
    loop = asyncio.get_running_loop()
    um_futures_client = UMFutures(key=key, secret=secret)
    func = partial(um_futures_client.get_position_risk, symbol=symbol, recvWindow=1000)
    try:
        response = await loop.run_in_executor(None, func)
        return response[0]
    except ClientError as error:
        logging.error(
            f"Found error. status(get_position){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(get_position){symbol}: {error}")


async def get_balance(key, secret):
    loop = asyncio.get_running_loop()
    um_futures_client = UMFutures(key=key, secret=secret)
    func = partial(um_futures_client.balance, recvWindow=1000)
    try:
        data = await loop.run_in_executor(None, func)
        usdt_data = next((item for item in data if item["asset"] == "USDT"), None)
        if usdt_data:
            balance = float(usdt_data["balance"])
            available_balance = float(usdt_data["availableBalance"])

            return [balance, available_balance]
        else:
            raise Exception("No data found for asset 'USDT'")
    except ClientError as error:
        logging.error(
            f"Found error. status(get_balance): {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(get_balance): {error}")


async def change_leverage(key, secret, symbol, leverage):
    loop = asyncio.get_running_loop()
    um_futures_client = UMFutures(key=key, secret=secret)
    func = partial(
        um_futures_client.change_leverage,
        symbol=symbol,
        leverage=leverage,
        recvWindow=1000,
    )
    try:
        await loop.run_in_executor(None, func)

    except ClientError as error:
        logging.error(
            f"Found error. status(change_leverage){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(change_leverage){symbol}: {error}")


async def open_position(
    key, secret, symbol, side, quantity, price, stopSide, profitPrice, stopPrice
):
    loop = asyncio.get_running_loop()
    now_timestamp = datetime.datetime.now(datetime.UTC).timestamp() * 1000
    timestamp = now_timestamp + (59 * 60 * 1000)
    timestamp = math.floor(timestamp)

    um_futures_client = UMFutures(key=key, secret=secret)
    func_open = partial(
        um_futures_client.new_order,
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        timeInForce="GTD",
        goodTillDate=timestamp,
        price=price,
    )
    func_tp = partial(
        um_futures_client.new_order,
        symbol=symbol,
        side=stopSide,
        type="TAKE_PROFIT_MARKET",
        stopPrice=profitPrice,
        closePosition="true",
    )
    func_sl = partial(
        um_futures_client.new_order,
        symbol=symbol,
        side=stopSide,
        type="STOP_MARKET",
        stopPrice=stopPrice,
        closePosition="true",
    )
    try:
        await loop.run_in_executor(None, func_open)
        await loop.run_in_executor(None, func_tp)
        await loop.run_in_executor(None, func_sl)

    except ClientError as error:
        logging.error(
            f"Found error. status(open_position){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(open_position){symbol}: {error}")


async def tp_sl(key, secret, symbol, side, quantity):
    loop = asyncio.get_running_loop()
    um_futures_client = UMFutures(key=key, secret=secret)
    func = partial(
        um_futures_client.new_order,
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
        reduceOnly="true",
    )
    try:
        await loop.run_in_executor(None, func)

    except ClientError as error:
        logging.error(
            f"Found error. status(tp_sl){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(tp_sl){symbol}: {error}")


async def cancel_orders(key, secret, symbol):
    loop = asyncio.get_running_loop()
    um_futures_client = UMFutures(key=key, secret=secret)
    func = partial(
        um_futures_client.cancel_open_orders,
        symbol=symbol,
        recvWindow=1000,
    )
    try:
        await loop.run_in_executor(None, func)

    except ClientError as error:
        logging.error(
            f"Found error. status(cancel_orders){symbol}: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}"
        )
    except Exception as error:
        logging.error(f"Unexpected error occurred(cancel_orders){symbol}: {error}")
