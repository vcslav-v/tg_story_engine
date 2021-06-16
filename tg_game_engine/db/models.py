"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TelegramUser(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)
    chapter_id = Column(Integer)
    message_id = Column(Integer)
    num_referals = Column(Integer, default=0)
    email = Column(Text)


class Media(Base):
    """Media."""

    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)

    file_id = Column(Text)
    uid = Column(Text)


class WaitReaction(Base):
    """Wait reactions."""

    __tablename__ = 'wait_reactions'

    id = Column(Integer, primary_key=True)

    name = Column(Text)
    uid = Column(Text)

    reactions = relationship(
        'Reaction',
        back_populates='wait_reaction',
        cascade='delete-orphan,delete',
    )


class Reaction(Base):
    """Reactions."""

    __tablename__ = 'reactions'

    id = Column(Integer, primary_key=True)

    text = Column(Text)

    wait_reaction_id = Column(
        Integer,
        ForeignKey('wait_reactions.id'),
    )

    wait_reaction = relationship(
        'WaitReaction',
        back_populates='reactions',
        passive_deletes=True,
    )


class Patron(Base):
    """Patron."""

    __tablename__ = 'patrons'

    id = Column(Integer, primary_key=True)

    email = Column(Text)
    status = Column(Text)
