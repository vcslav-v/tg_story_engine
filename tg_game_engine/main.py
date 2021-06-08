"""Main module gamemaster_bot project."""
import threading
from os import environ

import telebot
from flask import Flask, request

from tg_game_engine.worker import check_queue

APP_URL = environ.get('APP_URL') or ''
BOT_TOKEN = environ.get('BOT_TOKEN') or ''
REDIS = environ.get('REDIS_TLS_URL') or ''

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

from .handlers import message


@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([
            telebot.types.Update.de_json(
                request.stream.read().decode('utf-8')
            )
    ])
    return 'ok', 200


@app.route('/' + BOT_TOKEN, methods=['GET'])
def test():
    return 'ok', 200


url = APP_URL + BOT_TOKEN
if bot.get_webhook_info().url != url:
    bot.remove_webhook()
    bot.set_webhook(url)

thread = threading.Thread(target=check_queue.start)
thread.start()
