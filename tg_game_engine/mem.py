import redis
from tg_game_engine import schemas
from tg_game_engine.main import REDIS
from loguru import logger
from urllib.parse import urlparse

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


class UserContext:
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        self._wait_answer = f'{tg_id}:wait_answer'

    def set_wait_answers(self, message: schemas.Message):
        for key in r.keys(f'{self._wait_answer}:*'):
            r.delete(key)
        if not message.buttons:
            return
        for btn in message.buttons:
            r.set(f'{self._wait_answer}:{btn.text}', btn.next_message_id)

    def get_next_msg_id(self, user_msg: str = None):
        msg_id = r.get(f'{self._wait_answer}:{user_msg}')
        if msg_id and msg_id.isdecimal():
            return int(msg_id)
