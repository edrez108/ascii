import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, constr, conint


class User(BaseModel):
    phone_number: str
    password: str

    class Config:
        from_attribute = True


class DisplayUser(BaseModel):
    phone_number: str
    password: str

    class Config:
        from_attribute = True


class GetUser(BaseModel):
    phone_number: str

    class Config:
        from_attribute = True


class ChangeUserName(BaseModel):
    access_token: str
    id: str
    new_first_name: str
    new_last_name: str

    class Config:
        from_attribute = True


class BlockedUser(BaseModel):
    access_token: str
    id: str
    new_blocked_user: str
    new_blocked_channel: str
    new_blocked_group: str

    class Config:
        from_attribute = True


class CreateAccount(BaseModel):
    access_token: str
    name: str
    last_name: str
    profile_image_addr: str
    username: str
    bio: str
    phone_number: str
    blocked_users: Optional[list]
    blocked_channels: Optional[list]
    blocked_groups: Optional[list]


class SendTextMessage(BaseModel):
    access_token: str
    send_to: str
    message_id: Optional[str]
    title: str
    text: str
    sender_id: str
    receiver_id: str
    status: int
    send_at: Optional[str]
    seen_number: int
    deleted_by_owner: bool
    extera: Optional[list]

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True



class SendImageMessage(SendTextMessage):
    image_url: str
    image_size: str
    image_preview: str


class SendVoiceMessage(SendTextMessage):
    voice_url: str
    voice_size: str
    voice_length: str


class SendVideoMessage(SendTextMessage):
    video_url: str
    video_size: str
    video_length: str
    video_preview: str


class SendFileMessage(SendTextMessage):
    file_url: str
    file_size: str


class DeleteOwnerMessage(BaseModel):
    access_token: str
    delete_from: str
    user_id: str
    message_id: str

    class Config:

        from_attribute = True
        arbitrary_types_allowed = True


class DeletePrivateMessage(BaseModel):
    access_token: str
    message_id: str
    sender_id: str
    receiver_id: str

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True


class UpdateMessage(BaseModel):
    access_token: str
    message_id: str
    sender_id: str
    receiver_id: str
    new_text: str

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True


class CreateChat:
    pass


class CreateGroup(BaseModel):
    access_token: str
    name: str
    image_url: Optional[str]
    description: str
    channel_type: bool
    public_link: str
    created_at: str
    members: list
    admins: list
    add_left_dates: Optional[list]

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True



class CreateChannel(BaseModel):
    access_token: str
    name: str
    image_url: Optional[str]
    description: str
    channel_type: bool
    public_link: str
    created_at: str
    members: list
    admins: list

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True


class UpdateChannelInformation(BaseModel):
    access_token: str
    channel_id: str
    sender_id: str
    image_url: str
    name: str
    description: str
    channel_type: bool
    public_link: str

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True


class LeftGroup(BaseModel):
    access_token: str
    group_id: str
    user_id: str

    class Config:
        from_attribute = True
        arbitrary_types_allowed = True


class LeftChannel(BaseModel):
    pass


class DeletePrivateChat(BaseModel):
    pass


class UpdateMessageChannel(BaseModel):
    access_token: str
    sender_id: str
    channel_id: str
    message_id: str
    new_text: str

    class Confing:

        from_attribute = True
        arbitrary_types_allowed = True


class UpdateMessageGroup(BaseModel):
    access_token: str
    sender_id: str
    group_id: str
    message_id: str
    new_text: str

    class Confing:
        from_attribute = True
        arbitrary_types_allowed = True


class DeleteUser(BaseModel):
    access_token: str


class DeleteAccount(BaseModel):
    access_token: str
    id: str

