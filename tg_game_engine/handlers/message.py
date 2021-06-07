from loguru import logger
from tg_game_engine.db import tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.main import bot
from tg_game_engine.mem import UserContext


@logger.catch
@bot.message_handler(commands=['start'])
def start_message(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    tools.send_next_step(db, user_context)
    db.close()


@logger.catch
@bot.message_handler(
    content_types='text',
)
def text_reply(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    tools.send_next_step(db, user_context, msg.text)
    db.close()
