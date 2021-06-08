from loguru import logger
from time import sleep
import telebot
from os import environ

BOT_TOKEN = environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


while True:
    logger.debug('Here')
    sleep(10)
