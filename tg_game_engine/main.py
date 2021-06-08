"""Main module gamemaster_bot project."""
import threading
from os import environ

import telebot
from flask import Flask, request


APP_URL = environ.get('APP_URL') or ''
BOT_TOKEN = environ.get('BOT_TOKEN') or ''

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
