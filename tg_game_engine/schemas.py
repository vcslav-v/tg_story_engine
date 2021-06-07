from pydantic import BaseModel
from typing import Optional, List


class Button(BaseModel):
    text: str
    number: int
    next_message_id: int


class Message(BaseModel):
    id: int
    content_type: str
    chapter_id: int
    speed_type: int
    timeout: int
    text: Optional[str]
    media_uid: Optional[str]
    link: Optional[int]
    buttons: Optional[List[Button]]
    wait_reaction_uid: Optional[str]
    referal_block: Optional[int]
