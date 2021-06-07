"""Main module gamemaster_bot project."""
import telebot
from os import environ
from flask import Flask, request

APP_URL = environ.get('APP_URL')
BOT_TOKEN = environ.get('BOT_TOKEN')
REDIS = environ.get('REDIS')

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
bot.remove_webhook()
bot.set_webhook(url)