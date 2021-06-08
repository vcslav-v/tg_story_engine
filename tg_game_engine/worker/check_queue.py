from loguru import logger
from time import sleep


@logger.catch
def run():
    while True:
        logger.debug('Here')
        sleep(10)
