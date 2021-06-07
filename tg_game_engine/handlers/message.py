from tg_game_engine.main import bot
from tg_game_engine.db import tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.mem import UserContext


@bot.message_handler(commands=['start'])
def start_message(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    try:
        tools.send_next_step(db, user_context)
    except Exception as e:
        print(e)
    db.close()


@bot.message_handler(
    content_types='text',
)
def text_reply(msg):
    db = SessionLocal()
    user_context = UserContext(msg.from_user.id)
    tools.send_next_step(db, user_context, msg.text)
    db.close()
