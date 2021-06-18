from os import environ
from loguru import logger
import requests
from sqlalchemy.orm import Session
from tg_game_engine import schemas
from tg_game_engine.db import models
from tg_game_engine.mem import UserContext
from typing import Optional
from random import choice
DB_API_URL = environ.get('DB_API_URL') or ''


def set_patron_status(db: Session, email: str, status: str):
    exist_patron = db.query(models.Patron).filter_by(email=email).first()
    if exist_patron:
        exist_patron.status = status
    else:
        db.add(models.Patron(
            email=email,
            status=status,
        ))
    db.commit()


def add_referal(db: Session, tg_id: int):
    parrent_user: models.TelegramUser = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    parrent_user.num_referals = parrent_user.num_referals + 1
    db.commit()


def is_user_exist(db: Session, tg_id: int):
    return bool(db.query(models.TelegramUser).filter_by(telegram_id=tg_id).count())


def get_user(db: Session, tg_id: int) -> models.TelegramUser:
    tg_user = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    if not tg_user:
        tg_user = models.TelegramUser(telegram_id=tg_id)
        db.add(tg_user)
        db.commit()
    return tg_user


def is_patron(db: Session, user: models.TelegramUser) -> bool:
    if user.email:
        return bool(db.query(models.Patron).filter_by(email=user.email).count())
    return False


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


def get_reaction_msg(db: Session, uid: str) -> Optional[schemas.Message]:
    wait_reaction: models.WaitReaction = db.query(models.WaitReaction).filter_by(uid=uid).first()
    if not wait_reaction:
        return None
    return schemas.Message(
        content_type='text',
        speed_type=2000,
        timeout=0,
        text=choice(wait_reaction.reactions).text
    )


def get_message(
    db: Session,
    user: models.TelegramUser,
    user_context: UserContext,
    user_msg: str = None,
) -> schemas.Message:
    next_msg_id = user_context.get_next_msg_id(user_msg)
    if not next_msg_id:
        next_msg_id = user.message_id
    return get_message_by_id(db, next_msg_id)


def get_message_by_id(db: Session, msg_id: int = None) -> schemas.Message:
    req_url = f'{DB_API_URL}/msg/{msg_id}' if msg_id else DB_API_URL
    resp = requests.get(req_url)
    message: schemas.Message = schemas.Message.parse_raw(resp.text)
    if message.wait_reaction_uid:
        local_wait_reactions = db.query(
            models.WaitReaction
        ).filter_by(uid=message.wait_reaction_uid).first()
        if not local_wait_reactions:
            raw_wait_reactions = requests.get(
                f'{DB_API_URL}/wait_reactions/{message.wait_reaction_uid}'
            ).text
            wait_reactions: schemas.WaitReactions = schemas.WaitReactions.parse_raw(raw_wait_reactions)
            wait_reactions_model = models.WaitReaction(
                name=wait_reactions.name,
                uid=wait_reactions.uid,
            )
            db.add(wait_reactions_model)
            for react in wait_reactions.messages:
                db.add(models.Reaction(
                    text=react,
                    wait_reaction=wait_reactions_model,
                ))
            db.commit()
    return message


def set_email(db: Session, tg_id: int, email: str):
    user = get_user(db, tg_id)
    logger.debug(tg_id)
    logger.debug(email)
    logger.debug(user)
    if user:
        user.email = email
        db.commit()
