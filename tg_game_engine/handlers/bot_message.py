from loguru import logger
from tg_game_engine import bot_tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.main import bot
from tg_game_engine.mem import UserContext
from tg_game_engine.db.tools import add_referal
from tg_game_engine.db import tools as db_tools


def extract_link_data(text):
    data = {}
    if len(text.split()) <= 1:
        return data
    raw_data = text.split()[1].split('ZZ')
    for item in raw_data:
        key, *value = item.split('-')
        if value:
            data[key] = value[0]
    return data


@bot.message_handler(commands=['start'])
@logger.catch
def start_message(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    link_data = extract_link_data(msg.text)
    if link_data.get('ref') and link_data.get('ref').isdecimal():
        parrent_tg_id = int(link_data.get('ref'))
        is_parrent_exist = db_tools.is_user_exist(db, parrent_tg_id)
        is_new_user = not db_tools.is_user_exist(db, msg.from_user.id)
        if is_parrent_exist and is_new_user:
            parrent_user_context = UserContext(parrent_tg_id)
            add_referal(db, parrent_user_context.tg_id)
            bot_tools.send_next_step(db, parrent_user_context, check_block=False)
    bot_tools.send_next_step(db, user_context)
    db.close()


@bot.message_handler(
    content_types='text',
)
@logger.catch
def text_reply(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    bot_tools.send_next_step(db, user_context, msg.text)
    db.close()
