from tg_game_engine.db import models
from sqlalchemy.orm import Session
from tg_game_engine import schemas
import requests
from os import environ
from tg_game_engine.main import bot

DB_API_URL = environ.get('DB_API_URL') or ''


def get_user(db: Session, tg_id: int) -> models.TelegramUser:
    tg_user = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    if not tg_user:
        tg_user = models.TelegramUser(telegram_id=tg_id)
        db.add(tg_user)
        db.commit()
    return tg_user


def get_message(user: models.TelegramUser) -> schemas.Message:
    req_url = f'{DB_API_URL}/msg/{user.message_id}' if user.message_id else DB_API_URL
    resp = requests.get(req_url)
    return schemas.Message.parse_raw(resp.text)


def send(message: schemas.Message, user: models.TelegramUser):
    bot.send_message(user.telegram_id, message.text)


def send_next_step(db: Session, tg_id: int):
    user = get_user(db, tg_id)
    message = get_message(user)
    send(message, user)
