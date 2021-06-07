"""DataBase models."""
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TelegramUser(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)
    chapter_id = Column(Integer)
    message_id = Column(Integer)
    num_referals = Column(Integer, default=0)
