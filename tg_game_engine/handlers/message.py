from loguru import logger
from tg_game_engine import bot_tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.main import bot
from tg_game_engine.mem import UserContext
from tg_game_engine.db.tools import add_referal


def extract_link_data(text):
    if len(text.split()) <= 1:
        return
    raw_data = text.split()[1].split('ZZ')
    data = {}
    for item in raw_data:
        key, value = item.split('-')
        data[key] = value
    return data


@bot.message_handler(commands=['start'])
@logger.catch
def start_message(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    link_data = extract_link_data(msg.text)
    if link_data.get('ref') and link_data.get('ref').isdecimal():
        parrent_user_context = UserContext(int(link_data.get('ref')))
        add_referal(db, parrent_user_context.tg_id)
        bot_tools.send_next_step(db, user_context)
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
