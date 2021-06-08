from datetime import datetime
from os import environ
from urllib.parse import urlparse

import redis

from tg_game_engine import schemas

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
        self.send_next_message = f'{tg_id}:{SEND_NEXT_MSG}'
        self.send_msg_typing = f'{tg_id}:{SEND_MSG_TYPING}'

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

    def push_to_queue(self, message: schemas.Message):
        r.set(self.next_msg, message.json())
        r.set(self.next_msg_type, message.content_type)
        if message.content_type == 'text':
            typing_time = (len(message.text) / message.speed_type) * 60
        else:
            typing_time = MEDIA_SEND_SEC

        now_timestamp = int(datetime.timestamp(datetime.utcnow()))
        send_timestamp = now_timestamp + typing_time + message.timeout
        start_typing_timestamp = send_timestamp - typing_time
        r.zadd(MSG_QUEUE_PREFIX, {self.send_next_message: send_timestamp})
        r.zadd(MSG_QUEUE_PREFIX, {self.send_msg_typing: start_typing_timestamp})

    def get_next_msg_type(self) -> str:
        return r.get(self.next_msg_type)

    def get_next_msg(self) -> schemas.Message:
        return schemas.Message.parse_raw(r.get(self.next_msg))
