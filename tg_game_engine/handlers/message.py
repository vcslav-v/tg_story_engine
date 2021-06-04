from tg_game_engine.main import bot
from tg_game_engine.db import tools


@bot.message_handler(commands=['start'])
def start_message(msg):
    user = tools.get_user(msg.from_user.id)
    bot.send_message(msg.chat.id, user.telegram_id)


@bot.message_handler(
    content_types='text',
)
def text_reply(msg):
    bot.send_message(msg.text)
