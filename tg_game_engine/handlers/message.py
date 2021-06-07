from tg_game_engine.main import bot
from tg_game_engine.db import tools
from tg_game_engine.db.main import SessionLocal


@bot.message_handler(commands=['start'])
def start_message(msg):
    db = SessionLocal()
    user = tools.send_next_step(db, msg.from_user.id)
    bot.send_message(msg.chat.id, user.telegram_id)
    db.close()


@bot.message_handler(
    content_types='text',
)
def text_reply(msg):
    bot.send_message(msg.text)
