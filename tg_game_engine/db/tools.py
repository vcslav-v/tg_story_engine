from os import environ
from typing import Optional

import requests
from loguru import logger
from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException
from tg_game_engine import schemas
from tg_game_engine.db import models
from tg_game_engine.main import bot
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
    req_url = f'{DB_API_URL}/msg/{next_msg_id}' if next_msg_id else DB_API_URL
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


def get_media(db: Session, message: schemas.Message, try_get_local=True):
    media = db.query(models.Media).filter_by(uid=message.media_uid)
    if media and try_get_local:
        return media.file_id
    return requests.get(f'{DB_API_URL}/media/{message.media_uid}').content


def save_media(db: Session, message: schemas.Message, send_msg):
    if send_msg.content_type == 'photo':
        file_id = sorted(send_msg.photo, key=lambda item: item.width)[-1].file_id
    elif send_msg.content_type == 'voice':
        file_id = send_msg.voice
    elif send_msg.content_type == 'video_note':
        file_id = send_msg.video_note

    db.add(models.Media(
        uid=message.media_uid,
        file_id=file_id
    ))
    db.commit()


def send_media_msg(tg_ig: int, content_type: str, media, caption: Optional[str], buttons):
    if content_type == 'photo':
        return bot.send_photo(tg_ig, media, caption, reply_markup=buttons)
    elif content_type == 'audio':
        return bot.send_audio(tg_ig, media, caption, reply_markup=buttons)
    elif content_type == 'video_note':
        return bot.send_video_note(tg_ig, media, caption, reply_markup=buttons)


def send(db: Session, message: schemas.Message, user: models.TelegramUser):
    buttons = make_buttons(message)
    if message.content_type == 'text':
        bot.send_message(user.telegram_id, message.text, reply_markup=buttons)
    elif message.content_type in ['photo', 'audio', 'video_note']:
        media = get_media(db, message)
        try:
            send_msg = send_media_msg(
                user.telegram_id,
                message.content_type,
                media,
                message.text,
                buttons,
            )
        except ApiTelegramException:
            media = get_media(db, message, try_get_local=False)
            send_msg = send_media_msg(
                user.telegram_id,
                message.content_type,
                media,
                message.text,
                buttons,
            )

        if isinstance(media, bytes):
            save_media(db, message, send_msg)


def send_next_step(
    db: Session,
    user_context: UserContext,
    user_msg: str = None,
):
    user = get_user(db, user_context.tg_id)
    message = get_message(user, user_context, user_msg)
    send(db, message, user)
    user_context.set_wait_answers(message)
    user.message_id = message.id
    user.chapter_id = message.chapter_id
    db.commit()
