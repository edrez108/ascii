import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class Status(Enum):

    NOT_SEND = 1
    SEND = 2
    NOT_SEEN = 3
    SEEN = 4


class TextMessageFrame (BaseModel):
    title: str
    sender: str
    receiver: str
    status: Optional[int] = Status.NOT_SEND.value
    text: str
    sending_time: Optional[datetime.datetime] = datetime.datetime.now()
    deleted_by_owner: bool = False
    seen_nuber: int
    extera: Optional[list]

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "sender",
                "receiver": "receiver",
                "status": 1,
                "text": "some text ",
                "sending_time": "2020-10-15 23:59:59",
                "deleted_by_owner": False,
                "seen_number": 0,
                "extera": [{"like": None}, {"smile": None}]
            }

        }
        form_attribute = True


class SendMessageRequirement(BaseModel):
    collection_name: Optional[list]
    username_id: str

    class Config:
        form_attribute = True
        json_schema_extra = {
            "example": {
                "collection name": "message",
                "username_id": "ObjectID(oaooan3r5y09hrweofndodn)",
            }
        }


class FindMessage(SendMessageRequirement):
    message_id: str

    class Config:
        form_attribute = True
        json_schema_extra = {
            "example": {
                "collection name": "message",
                "username_id": "ObjectID(oaooan3r5y09hrweofndodn)",
                "message_id": "ObjectID(ofno5ytt0tnoedoirn32roirn)",
            }
        }


class SendMessage_CG(BaseModel):
    text: str
    status: Optional[int] = Status.NOT_SEND.value
    sending_time: Optional[datetime.datetime] = datetime.datetime.now()

    class Config:
        json_schema_extra = {
            "example": {
                "text": "some text",
                "receiver": " receiver",
                "status": "' 1 , 2 , 3 , 4 , 5 , 6",
                "sending_time": "2020-10-15 23:59:59"
            }

        }
        form_attribute = True
