"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text, LargeBinary, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TelegramUser(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)
    message_id = Column(Integer)
    num_referals = Column(Integer, default=0)
    email = Column(Text)


class Message(Base):
    """Story."""

    __tablename__ = 'messages'

    link = Column(Text, unique=True, primary_key=True, autoincrement=False)
    start_msg = Column(Boolean, default=False)
    timeout = Column(Integer, default=400)
    speed_type = Column(Integer, default=1200)
    content_type = Column(Text)
    message = Column(Text)
    media = relationship(
        'Media',
        uselist=False,
        back_populates='parrent_message',
        cascade='delete-orphan,delete',
        foreign_keys='[Media.parrent_message_link]',
    )
    next_msg = Column(Text, ForeignKey('messages.link'))
    buttons = relationship(
        'Button',
        back_populates='parrent_message',
        cascade='delete-orphan,delete',
        foreign_keys='[Button.parrent_message_link]',
    )
    wait_reaction_id = Column(Integer, ForeignKey('wait_reactions.id'))
    wait_reaction = relationship('WaitReaction')
    referal_block = Column(Integer, default=0)


class Button(Base):
    """Buttons."""

    __tablename__ = 'buttons'

    id = Column(Integer, primary_key=True)

    text = Column(Text, nullable=False)
    parrent_message_link = Column(
        Text,
        ForeignKey('messages.link'),
        nullable=False,
    )
    parrent_message = relationship(
        'Message',
        back_populates='buttons',
        foreign_keys=[parrent_message_link],
    )
    number = Column(Integer)

    next_message_link = Column(Text, ForeignKey('messages.link'))
    next_message = relationship(
        'Message',
        foreign_keys=[next_message_link],
    )


class Media(Base):
    """Media."""

    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)

    file_data = Column(LargeBinary, nullable=False)
    tg_id = Column(Text)
    parrent_message_link = Column(
        Text,
        ForeignKey('messages.link'),
        nullable=False,
    )
    parrent_message = relationship(
        'Message',
        back_populates='media',
        foreign_keys=[parrent_message_link]
    )


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
