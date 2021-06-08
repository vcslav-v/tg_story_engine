from os import environ
from loguru import logger
import requests
from sqlalchemy.orm import Session
from tg_game_engine import schemas
from tg_game_engine.db import models
from tg_game_engine.mem import UserContext

DB_API_URL = environ.get('DB_API_URL') or ''


def get_user(db: Session, tg_id: int) -> models.TelegramUser:
    tg_user = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    if not tg_user:
        tg_user = models.TelegramUser(telegram_id=tg_id)
        db.add(tg_user)
        db.commit()
    return tg_user


def get_media(db: Session, message: schemas.Message, try_get_local=True):
    media = db.query(models.Media).filter_by(uid=message.media_uid).first()
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


def get_message(
    user: models.TelegramUser,
    user_context: UserContext,
    user_msg: str = None,
) -> schemas.Message:
    next_msg_id = user_context.get_next_msg_id(user_msg)
    if not next_msg_id:
        next_msg_id = user.message_id
    req_url = f'{DB_API_URL}/msg/{next_msg_id}' if next_msg_id else DB_API_URL
    logger.debug(req_url)
    resp = requests.get(req_url)
    return schemas.Message.parse_raw(resp.text)
