import logging, datetime, math
from binance.um_futures import UMFutures
from binance.error import ClientError
import Config


def get_position(key, secret, symbol):
    um_futures_client = UMFutures(key=key, secret=secret)

    try:
        response = um_futures_client.get_position_risk(symbol=symbol, recvWindow=1000)
        return response[0]
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


def get_balance(key, secret):
    um_futures_client = UMFutures(key=key, secret=secret)
    try:
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


def change_leverage(key, secret, symbol, leverage):
    um_futures_client = UMFutures(key=key, secret=secret)
    try:
        um_futures_client.change_leverage(
            symbol=symbol, leverage=leverage, recvWindow=1000
        )
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


def open_position(key, secret, symbol, side, quantity, price, stopSide, stopPrice):
    now_timestamp = datetime.datetime.now(datetime.UTC).timestamp() * 1000
    timestamp = now_timestamp + (57 * 60 * 1000)
    timestamp = math.floor(timestamp)

    um_futures_client = UMFutures(key=key, secret=secret)
    try:
        um_futures_client.new_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            timeInForce="GTD",
            goodTillDate=timestamp,
            price=price,
        )
        # 손절로직
        um_futures_client.new_order(
            symbol=symbol,
            side=stopSide,
            type="STOP_MARKET",
            stopPrice=stopPrice,
            closePosition="true",
        )

    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


def tp_sl(key, secret, symbol, side, quantity):
    um_futures_client = UMFutures(key=key, secret=secret)
    try:
        um_futures_client.new_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
            reduceOnly="true",
        )

    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
