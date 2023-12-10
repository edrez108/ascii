import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from Authjwt import JWT
# from message.Models import SendMessage
# from Database import collection
from enum import Enum
Route = APIRouter(
    tags=["Message"],
    prefix="/Message"
)


class Status(Enum):

    NOT_SEND = 1
    SEND = 2
    NOT_SEEN = 3
    SEEN = 4
#
#
# @Route.post("/send")
# async def send_message(token: dict, request: SendMessage):
#     test = request
#     test.sending_time = str(test.sending_time)
#     test = dict(request)
#     try:
#         username = JWT.decode_jwt(token["access_token"])
#         test["sender"] = username
#         test["sending_time"] = str(datetime.datetime.now())
#         test["status"] = Status.SEND
#         collection.insert_one(dict(test))
#         return JSONResponse(status_code=status.HTTP_200_OK,
#                             content=dict(test))
#     except :
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="message not send")
