from datetime import datetime
from os import environ
from urllib.parse import urlparse
from loguru import logger
import redis
from typing import List

from tg_game_engine import schemas
from tg_game_engine.main import BOT_USERNAME

REDIS = environ.get('REDIS_TLS_URL') or ''

parsed_redis_url = urlparse(REDIS)
r = redis.Redis(
    host=parsed_redis_url.hostname,
    port=parsed_redis_url.port,
    username=parsed_redis_url.username,
    password=parsed_redis_url.password,
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True,
)

MSG_QUEUE_PREFIX = 'queue'
SEND_NEXT_MSG = 'send_next_message'
SEND_MSG_TYPING = 'send_message_typing'
MEDIA_SEND_SEC = 4


def queue():
    return r.zscan_iter(MSG_QUEUE_PREFIX)


def rem_from_queue(key: str):
    r.zrem(MSG_QUEUE_PREFIX, key)


def push_back_to_queue(command, timestamp):
    r.zadd(MSG_QUEUE_PREFIX, {command: timestamp})


class UserContext:
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        self.wait_answer = f'{tg_id}:wait_answers'
        self.next_msg = f'{tg_id}:next_msg'
        self.next_msg_type = f'{tg_id}:next_msg_type'
        self.wait_reaction_uid = f'{tg_id}:wait_reaction_uid'
        self.block_msg_stage = f'{tg_id}:block_msg'
        self.send_next_message = f'{tg_id}:{SEND_NEXT_MSG}'
        self.send_msg_typing = f'{tg_id}:{SEND_MSG_TYPING}'

        self.format = {'ref_url': f'https://t.me/{BOT_USERNAME}?start=ref-{tg_id}'}

    def set_wait_answers(self, message: schemas.Message):
        for key in r.keys(f'{self.wait_answer}:*'):
            r.delete(key)
        if not message.buttons:
            return
        for btn in message.buttons:
            r.set(f'{self.wait_answer}:{btn.text}', btn.next_message_id)

    def get_next_msg_id(self, user_msg: str = None):
        msg_id = r.get(f'{self.wait_answer}:{user_msg}')
        if msg_id and msg_id.isdecimal():
            return int(msg_id)

    def set_next_msg(self, message: schemas.Message):
        r.set(self.next_msg, message.json())
        r.set(self.next_msg_type, message.content_type)
        if message.wait_reaction_uid:
            r.set(self.wait_reaction_uid, message.wait_reaction_uid)

    def push_to_queue(self, message: schemas.Message):
        self.set_next_msg(message)
        if message.content_type == 'text':
            typing_time = int((len(message.text) / message.speed_type) * 60)
        else:
            typing_time = MEDIA_SEND_SEC

        now_timestamp = int(datetime.timestamp(datetime.utcnow()))
        send_timestamp = now_timestamp + typing_time + message.timeout
        start_typing_timestamp = send_timestamp - typing_time
        r.zadd(MSG_QUEUE_PREFIX, {self.send_next_message: send_timestamp})
        for index, type_time in enumerate(range(start_typing_timestamp, send_timestamp, 5)):
            r.zadd(MSG_QUEUE_PREFIX, {f'{self.send_msg_typing}:{index}': type_time})

    def get_next_msg_type(self) -> str:
        return r.get(self.next_msg_type)

    def get_next_msg(self) -> schemas.Message:
        return schemas.Message.parse_raw(r.get(self.next_msg))

    def get_reaction_uid(self) -> str:
        return r.get(self.wait_reaction_uid)

    def is_msg_in_queue(self):
        cursor, items = r.zscan(MSG_QUEUE_PREFIX, match=f'{self.tg_id}:{SEND_NEXT_MSG}')
        if items:
            return True
        return False

    def block_msg(self):
        r.set(self.block_msg_stage, '1')

    def deblock_msg(self):
        r.delete(self.block_msg_stage)

    def is_blocked(self):
        return bool(r.exists(self.block_msg_stage))
