from loguru import logger
from tg_game_engine import bot_tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.main import bot
from tg_game_engine.mem import UserContext


@bot.message_handler(commands=['start'])
@logger.catch
def start_message(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
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
