from tg_game_engine.db import models
from sqlalchemy.orm import Session
from tg_game_engine import schemas
import requests
from os import environ
from tg_game_engine.main import bot
from telebot import types
from tg_game_engine.mem import UserContext

DB_API_URL = environ.get('DB_API_URL') or ''


def get_user(db: Session, tg_id: int) -> models.TelegramUser:
    tg_user = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    if not tg_user:
        tg_user = models.TelegramUser(telegram_id=tg_id)
        db.add(tg_user)
        db.commit()
    return tg_user


def get_message(
    user: models.TelegramUser,
    user_context: UserContext,
    user_msg: str = None,
) -> schemas.Message:
    next_msg_id = user_context.get_next_msg_id(user_msg)
    if not next_msg_id:
        next_msg_id = user.message_id
    req_url = f'{DB_API_URL}/msg/{user.message_id}' if next_msg_id else DB_API_URL
    resp = requests.get(req_url)
    return schemas.Message.parse_raw(resp.text)


def make_buttons(message: schemas.Message) -> types.ReplyKeyboardMarkup:
    if not message.buttons:
        return
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    for button in message.buttons:
        keyboard.add(button.text)
    return keyboard


def send(message: schemas.Message, user: models.TelegramUser):
    buttons = make_buttons(message)
    bot.send_message(user.telegram_id, message.text, reply_markup=buttons)


def send_next_step(db: Session, user_context: UserContext, user_msg: str = None):
    print('start')
    user = get_user(db, user_context.tg_id)
    print('user')
    message = get_message(user, user_context, user_msg)
    print('message')
    send(message, user)
    print('send')
    user_context.set_wait_answers(message)
    print('set_wait_answers')
    user.message_id = message.id
    print('message_id')
    user.chapter_id = message.chapter_id
    print('chapter_id')
    db.commit()
