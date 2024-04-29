import datetime, logging
import asyncio


# 로그 기록 함수
def setup_logging():
    # 로거 객체 생성, 로그 레벨을 DEBUG로 설정하여 모든 로그를 캡처.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # INFO 레벨의 로그를 기록하는 파일 핸들러
    info_file_handler = logging.FileHandler("logs/info_logs.log")
    info_file_handler.setLevel(logging.INFO)
    info_file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    info_file_handler.setFormatter(info_file_formatter)
    logger.addHandler(info_file_handler)

    # ERROR 레벨 이상의 로그를 기록하는 파일 핸들러
    file_handler = logging.FileHandler("logs/error_logs.log")
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


# 간격에 따라 다음 정시까지 대기하는 함수
async def wait_until_next_interval(interval):
    now = datetime.datetime.now(datetime.UTC)
    if interval == "1h":
        next_time = (
            now.replace(minute=0, second=0, microsecond=0)
            + datetime.timedelta(hours=1)
            + datetime.timedelta(seconds=1)
        )

    elif interval == "4h":
        hours_until_next = 4 - now.hour % 4
        hours_until_next = 4 if hours_until_next == 0 else hours_until_next
        next_time = (
            now.replace(minute=0, second=0, microsecond=0)
            + datetime.timedelta(hours=hours_until_next)
            + datetime.timedelta(seconds=1)
        )
    elif interval == "1d":
        next_time = (
            now.replace(hour=0, minute=0, second=0, microsecond=0)
            + datetime.timedelta(days=1)
            + datetime.timedelta(seconds=1)
        )

    wait_seconds = (next_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)


# 소수점 세 자리까지 포맷
def divide_and_format(value):
    result = value / 3
    formatted_result = float(format(result, ".3f"))
    return formatted_result
