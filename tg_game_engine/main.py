"""Main module gamemaster_bot project."""
import threading
from os import environ
from loguru import logger
import telebot
from flask import Flask

APP_URL = environ.get('APP_URL') or ''
BOT_TOKEN = environ.get('BOT_TOKEN') or ''

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

BOT_USERNAME = bot.get_me().username

from .handlers import bot_message, web


def run_workers():
    def check_queue_worker():
        from tg_game_engine.worker import check_queue
        check_queue.start()

    thread = threading.Thread(target=check_queue_worker)
    thread.start()


url = APP_URL + BOT_TOKEN
if bot.get_webhook_info().url != url:
    bot.remove_webhook()
    bot.set_webhook(url)

run_workers()
