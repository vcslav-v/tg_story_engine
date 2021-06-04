from tg_game_engine.db.main import SessionLocal
from tg_game_engine.db import models


def get_user(tg_id: int):
    db = SessionLocal()
    tg_user = db.query(models.TelegramUser).filter_by(telegram_id=tg_id).first()
    if not tg_user:
        tg_user = models.TelegramUser(telegram_id=tg_id)
        db.add(tg_user)
        db.commit()
    db.close()
    return tg_user
