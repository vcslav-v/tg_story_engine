from pydantic import BaseModel
from typing import Optional, List


class Button(BaseModel):
    text: str
    number: int
    next_message_link: str


class Message(BaseModel):
    link: str
    content_type: str = 'text'
    speed_type: int
    timeout: int
    text: Optional[str]
    media_id: Optional[int]
    next_msg: Optional[str]
    buttons: Optional[List[Button]]
    wait_reaction_uid: Optional[str]
    referal_block: Optional[int]


class WaitReactions(BaseModel):
    name: str
    uid: str
    messages: List[str]