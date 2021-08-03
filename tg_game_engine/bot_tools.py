from typing import Optional

from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException
from loguru import logger
from tg_game_engine import schemas
from tg_game_engine.db import models, tools
from tg_game_engine.main import bot, APP_URL
from tg_game_engine.mem import UserContext


def make_buttons(message: schemas.Message) -> types.ReplyKeyboardMarkup:
    if not message.buttons:
        return
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    for button in message.buttons:
        keyboard.add(button.text)
    return keyboard


def send_media_msg(tg_ig: int, content_type: str, media, caption: Optional[str], buttons):
    if content_type == 'photo':
        return bot.send_photo(tg_ig, media, caption, reply_markup=buttons)
    elif content_type == 'audio':
        return bot.send_audio(tg_ig, media, caption, reply_markup=buttons)
    elif content_type == 'video_note':
        return bot.send_video_note(tg_ig, media, caption, reply_markup=buttons)


def send(
    db: Session,
    message: schemas.Message,
    user: models.TelegramUser,
    user_context: UserContext
):
    buttons = make_buttons(message)
    if message.content_type == 'text':
        bot.send_message(
            user.telegram_id,
            message.text.format_map(user_context.format),
            reply_markup=buttons
        )
    elif message.content_type in ['photo', 'audio', 'video_note']:
        media = tools.get_media(db, message)
        try:
            send_msg = send_media_msg(
                user.telegram_id,
                message.content_type,
                media,
                message.text,
                buttons,
            )
        except ApiTelegramException:
            media = tools.get_media(db, message, try_get_local=False)
            send_msg = send_media_msg(
                user.telegram_id,
                message.content_type,
                media,
                message.text,
                buttons,
            )

        if isinstance(media, bytes):
            tools.save_media(db, message, send_msg)


def send_next_step(
    db: Session,
    user_context: UserContext,
    user_msg: str = None,
    check_block: bool = True
):
    user = tools.get_user(db, user_context.tg_id)
    if user_context.is_msg_in_queue() or (user_context.is_blocked() and check_block):
        reaction_msg = tools.get_reaction_msg(db, user_context.get_reaction_uid())
        if reaction_msg:
            send(db, reaction_msg, user, user_context)
        return
    message = tools.get_message(db, user, user_context, user_msg)
    if message:
        logger.debug(message)
        user_context.push_to_queue(message)


def send_status(tg_id: int, content_type: str):
    if content_type == 'text':
        action = 'typing'
    elif content_type == 'photo':
        action = 'upload_photo'
    elif content_type == 'voice':
        action = 'record_audio'
    elif content_type == 'video_note':
        action = 'record_video_note'
    bot.send_chat_action(tg_id, action)
