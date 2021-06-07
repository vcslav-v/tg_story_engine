import redis
from tg_game_engine import schemas
from tg_game_engine.main import REDIS


r = redis.Redis(
    host=REDIS,
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

    def get_next_msg_id(self, user_msg: str):
        try:
            msg_id = int(r.get(f'{self._wait_answer}:{user_msg}'))
        except Exception:
            return
        return msg_id
