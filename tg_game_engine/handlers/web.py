import json

import telebot
from flask import request
from loguru import logger
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.db.tools import set_patron_status
from tg_game_engine.main import BOT_TOKEN, app, bot


@app.route('/' + BOT_TOKEN, methods=['POST'])
@logger.catch
def getMessage():
    try:
        bot.process_new_updates([
                telebot.types.Update.de_json(
                    request.stream.read().decode('utf-8')
                )
        ])
        return 'ok', 200
    except:
        return 'incorrect', 400


@app.route('/' + BOT_TOKEN, methods=['GET'])
def test():
    return 'ok', 200


@app.route("/patreon/", methods=['POST'])
def patreon():
    db = SessionLocal()
    data = json.loads(request.stream.read().decode("utf-8"))
    email = data['data']['attributes']['email']
    status = data['data']['attributes']['patron_status']
    set_patron_status(db, email, status)
    db.close()
    return 'ok', 200
