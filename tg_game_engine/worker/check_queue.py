from loguru import logger
from time import sleep
from tg_game_engine import mem
from datetime import datetime
from tg_game_engine import bot_tools
from tg_game_engine.db import tools as db_tools
from tg_game_engine.db.main import SessionLocal


@logger.catch
def start():
    while True:
        now_timestamp = int(datetime.timestamp(datetime.utcnow()))
        try:
            for command, timestamp in mem.queue():
                if now_timestamp >= timestamp:
                    mem.rem_from_queue(command)
                    run(command)
                else:
                    break
        except Exception as e:
            logger.debug(e)


@logger.catch
def run(command: str):
    raw_user_id, call_to, *tail = command.split(':')
    user_id = int(raw_user_id)
    user_context = mem.UserContext(user_id)
    if call_to == mem.SEND_MSG_TYPING:
        bot_tools.send_status(user_id, user_context.get_next_msg_type())

    elif call_to == mem.SEND_NEXT_MSG:
        db = SessionLocal()
        user = db_tools.get_user(db, user_id)
        message = user_context.get_next_msg()
        is_ref_block = message.referal_block and message.referal_block > user.num_referals
        is_patron = db_tools.is_patron(db, user)
        if is_ref_block and not is_patron:
            user_context.block_msg()
            db.close()
            return
        if user_context.is_blocked():
            user_context.deblock_msg()
        bot_tools.send(db, message, user, user_context)
        if message.buttons:
            user_context.set_wait_answers(message)
        elif message.link:
            link_message = db_tools.get_message_by_id(db, message.link)
            user_context.push_to_queue(link_message)
        user.message_id = message.id
        user.chapter_id = message.chapter_id
        db.commit()
        db.close()
