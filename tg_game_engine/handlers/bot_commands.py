from loguru import logger
from tg_game_engine import bot_tools
from tg_game_engine.db.main import SessionLocal
from tg_game_engine.main import bot, PATREON_URL, ADMIN_ID
from tg_game_engine.mem import UserContext
from tg_game_engine.db import tools as db_tools


@bot.message_handler(commands=['im_patron'])
@logger.catch
def get_email(msg):
    message = bot.reply_to(msg, 'Введите email указанный на Patreon.')
    bot.register_next_step_handler(message, set_email)


@bot.message_handler(commands=['admin'])
@logger.catch
def admin_status(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    db = SessionLocal()
    rows = []
    rows.append(f'Игроков - {db_tools.count_users(db)}')
    bot.send_message(msg.from_user.id, '\n'.join(rows))
    db.close()


@bot.message_handler(commands=['add_ref'])
@logger.catch
def admin_add_ref(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    message = bot.reply_to(msg, 'Кому добавить реферала?')
    bot.register_next_step_handler(message, add_ref)


@logger.catch
def add_ref(msg):
    if msg.from_user.id != ADMIN_ID or not msg.text.isdecimal():
        return
    db = SessionLocal()
    user = db_tools.get_user(db, int(msg.text))
    user.num_referals += 1
    db.commit()
    user_context = UserContext(int(msg.text))
    bot_tools.send_next_step(db, user_context, check_block=False)
    db.close()
    bot.send_message(msg.from_user.id, 'done')


@logger.catch
def set_email(msg):
    db = SessionLocal()
    user = db_tools.get_user(db, msg.from_user.id)
    user.email = msg.text
    db.commit()
    user_context = UserContext(msg.from_user.id)
    if db_tools.is_patron(db, user):
        status_msg = 'Ваш статус "Патрон" - Спасибо!'
    else:
        status_msg = f'Станьте Патроном и получите полный доступ! - {PATREON_URL}'
    bot.send_message(msg.from_user.id, status_msg)
    bot_tools.send_next_step(db, user_context, check_block=False)
    db.close()


@bot.message_handler(commands=['status'])
@logger.catch
def get_status(msg):
    db = SessionLocal()
    user = db_tools.get_user(db, msg.from_user.id)
    rows = []
    # if db_tools.is_patron(db, user):
    #     rows.append('Ваш статус "Патрон" - Спасибо!')
    # else:
    #     rows.append(f'Станьте Патроном и получите полный доступ! - {PATREON_URL}')
    rows.append(f'Вы привели {user.num_referals} игроков.')
    bot.send_message(msg.from_user.id, '\n'.join(rows))
    db.close()


@bot.message_handler(commands=['reset'])
@logger.catch
def reset(msg):
    db = SessionLocal()
    db_tools.reset_story(db, msg.from_user.id)
    user_context = UserContext(msg.from_user.id)
    user_context.flush()
    bot_tools.send_next_step(db, user_context)
    db.close()


@bot.message_handler(commands=['reset_chapter'])
@logger.catch
def reset_chapter(msg):
    db = SessionLocal()
    db_tools.reset_chapter(db, msg.from_user.id)
    user_context = UserContext(msg.from_user.id)
    user_context.flush()
    bot_tools.send_next_step(db, user_context)
    db.close()
