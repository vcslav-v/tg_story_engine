from tg_game_engine.main import bot


@bot.message_handler(commands=['start'])
def start_message(msg):
    bot.send_message(msg.chat.id, 'hi')
