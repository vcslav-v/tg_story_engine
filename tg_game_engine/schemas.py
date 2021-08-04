from pydantic import BaseModel
from typing import Optional, List


class Button(BaseModel):
    text: str
    number: int
    next_message_id: int


class Message(BaseModel):
    id: Optional[int]
    content_type: str = 'text'
    chapter_id: Optional[int]
    speed_type: int
    timeout: int
    text: Optional[str]
    media_uid: Optional[str]
    link: Optional[int]
    buttons: Optional[List[Button]]
    wait_reaction_uid: Optional[str]
    referal_block: Optional[int]


class WaitReactions(BaseModel):
    name: str
    uid: str
    messages: List[str]