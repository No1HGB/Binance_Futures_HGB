import logging, datetime, math
from binance.um_futures import UMFutures
from binance.error import ClientError
from util import setup_logging
import Config


def get_positions(key, secret):
    setup_logging()

    try:
        client = UMFutures(key=key, secret=secret)
        symbols = Config.symbols
        data = client.account(recvWindow=1000)
        all_positions = data["positions"]
        positions = [
            position for position in all_positions if position["symbol"] in symbols
        ]
        return positions
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return None


def get_balance(key, secret):
    setup_logging()

    try:
        um_futures_client = UMFutures(key=key, secret=secret)
        data = um_futures_client.balance(recvWindow=1000)
        usdt_data = next((item for item in data if item["asset"] == "USDT"), None)
        if usdt_data:
            balance = float(usdt_data["balance"])
            available_balance = float(usdt_data["availableBalance"])

            return [balance, available_balance]
        else:
            print("No data found for asset 'USDT'")
            return None
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return None


def open_trade(key, secret, symbol, side, balance, price):
    setup_logging()
    now_timestamp = datetime.datetime.now(datetime.UTC).timestamp() * 1000
    timestamp = now_timestamp + (57 * 60 * 1000)
    timestamp = math.floor(timestamp)

    ratio = Config.margin
    raw_quantity = balance * (ratio / 100) / price
    quantity = math.trunc(raw_quantity * 1000) / 1000

    try:
        um_futures_client = UMFutures(key=key, secret=secret)
        um_futures_client.new_order_test(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            timeInForce="GTD",
            goodTillDate=timestamp,
            price=price,
        )

    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
