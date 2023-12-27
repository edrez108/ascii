import json

from fastapi import APIRouter, Depends, status, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import json
from sqlalchemy import text
import Authjwt.JWT
import Database
import user.Models as User_models
import user.Schema as User_Schema
import user.Services as User_Services
import user.Validation as User_Validation
from Authjwt import JWT
from enum import Enum
from message.Models import SendMessage_CG
import datetime
from Database import get_mongo_db, get_mongo_database, collection_dict, init_collection, client
from message.Schema import message_serializer, messages_serializer, cgs_serializer

## 111111111111111111111111111111111111111111111

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/user", tags=['users'])

class Status(Enum):

    NOT_SEND = 1
    SEND = 2
    SEEN = 3


#  #####################################################################################################################

@router.get("/")
async def root():
    return {"message": "fetching aoansdoasdnaosdjnasodjnasojdna"}





@router.post("/signup", status_code=status.HTTP_200_OK)
async def create_user(request: User_Schema.User, database: Session = Depends(Database.get_database)):
    user = await User_Validation.verify_existing_user(request.phone_number, database)
    if not user:

        return await User_Services.create_user(request, database)

    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Already Exist !!!")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: User_Schema.DisplayUser, database: Session = Depends(Database.get_database)):

    user = await User_Validation.verify_existing_user(request.phone_number, database)


    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Dose not Exist !!!")
    # db_pass = database.execute(text(f"SELECT password FROM public.users WHERE phone_number = '{user.phone_number}'")).first().t[0]
    if await JWT.verify_password(request.password, user.password):
        return await JWT.sign_jwt(user.phone_number)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=" password dose not  match")


@router.post("/get_all_users", status_code=status.HTTP_200_OK)
async def get_all_users(request: dict, database: Session = Depends(Database.get_database)):
    token_user = await JWT.decode_jwt(request["access_token"])
    if token_user:
        await User_Services.get_users(database)
        return True
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=" UNAUTHORIZERD...")




@router.post("/delete_user")
async def delete_user(request: dict, database: Session = Depends(Database.get_database)):
    token_user = await JWT.decode_jwt(request["access_token"])
    if token_user:
        response = await User_Services.delete_user(phone_number=token_user, database=database)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="user Dose not exist")


@router.post("/create_account")
async def create_account(request: User_Schema.CreateAccount, collection: get_mongo_database = Depends(get_mongo_database)):
    token_user = await JWT.decode_jwt(request.access_token)
    if token_user:
        content = await User_Services.create_account(request, collection)

        if content:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"id": content})
    else:
        JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expires")


@router.post("/change_password")
async def change_password(token: dict, password: dict, collection: get_mongo_database = Depends(get_mongo_database),
                          database: Session = Depends(Database.get_database)):
    token_user = await Authjwt.JWT.decode_jwt(token["access_token"])
    if token_user:
        password


@router.delete("/delete_account")
async def delete_account(request: User_Schema.DeleteAccount,
                         collection: get_mongo_database = Depends(get_mongo_database)):
    token_user = await Authjwt.JWT.decode_jwt(request["access_token"])
    try:
        if token_user:
            response = await User_Services.delete_account(request.id, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="token Expired")

    except BaseException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=" something went wrong")


@router.get("/update_last_seen")
async def update_last_seen(collection: get_mongo_database = Depends(get_mongo_database)):
    pass


@router.post("/change_name")
async def update_user_first_last_names(request: User_Schema.ChangeUserName,
                                       collection: get_mongo_database = Depends(get_mongo_database)):
    token_user = await Authjwt.JWT.decode_jwt(request.access_token)
    if token_user:
        return await User_Services.update_last_seen(request, collection)
    else:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")


@router.post("/add_blocked")
async def add_blocked_user_channel_group(request: User_Schema.BlockedUser,
                                         collection: get_mongo_database = Depends(get_mongo_database)):
    token_user = await Authjwt.JWT.decode_jwt(request.access_token)
    if token_user:

        return await User_Services.add_blocked(request, collection)
    else:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=" Token Expired")

# ######################################################################################################################


@router.post("/send_private_message")
async def send_private_message(request: User_Schema.SendTextMessage,
                       collection: get_mongo_database = Depends(get_mongo_database)):

    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:

            content = await User_Services.send_private_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"message sent with id {content}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")
    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.post("/send_channel_message")
async def send_channel_message(request: User_Schema.SendTextMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:

            content = await User_Services.send_channel_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"message sent with id {content}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})
# @router.post("/send_image")
# async def send_image_message(request: User_Schema.SendImageMessage, collection: get_mongo_database = Depends(get_mongo_database)):
#
#     try:
#         token_user = await JWT.decode_jwt(request.access_token)
#         if token_user:
#
#             content = await User_Services.send_image_message(request, collection)
#             return JSONResponse(status_code=status.HTTP_200_OK, content=f"image Message sent with id {content}")
#         else:
#             return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")
#     except BaseException as error:
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})
#
#
#
# @router.post("/send_video")
# async def send_video_message(request: User_Schema.SendVideoMessage, collection: get_mongo_database = Depends(get_mongo_database)):
#     try:
#         token_user = await JWT.decode_jwt(request.access_token)
#         if token_user:
#             content = await User_Services.send_video_message(request, collection)
#             return JSONResponse(status_code=status.HTTP_200_OK, content=f"Video Message sent with id {content}")
#         else:
#             return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")
#
#     except BaseException as error:
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})
#
#
# @router.post("/send_voice")
# async def send_voice_message(request: User_Schema.SendVoiceMessage, collection: get_mongo_database = Depends(get_mongo_database)):
#     try:
#         token_user = await JWT.decode_jwt(request.access_token)
#         if token_user:
#             content = await User_Services.send_voice_message(request, collection)
#             return JSONResponse(status_code=status.HTTP_200_OK, content=f"voice Message sent with id {content}")
#         else:
#             return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")
#
#     except BaseException as error:
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})
#
#
# @router.post("/send_file")
# async def send_file_message(request: User_Schema.SendFileMessage, collection: get_mongo_database = Depends(get_mongo_database)):
#     try:
#         token_user = await JWT.decode_jwt(request.access_token)
#         if token_user:
#             content = await User_Services.send_file_message(request, collection)
#             return JSONResponse(status_code=status.HTTP_200_OK, content=f"File Message sent with id {content}")
#         else:
#             return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")
#
#     except BaseException as error:
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.delete("/delete_owner_message")
async def delete_owner_message(request: User_Schema.DeleteOwnerMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)

        if token_user:
            response = await User_Services.delete_for_owner(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"Message Deleted with id {response}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.delete("/delete_private_message")
async def delete_private_message(request: User_Schema.DeletePrivateMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.delete_private_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"Message Deleted with id {response}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.delete("/delete_channel_message")
async def delete_channel_message(request: User_Schema.DeletePrivateMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.delete_channel_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"Message Deleted with id {response}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.delete("/delete_group_message")
async def delete_group_message(request: User_Schema.DeletePrivateMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.delete_group_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"Message Deleted with id {response}")
        else:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": error})


@router.post("/edit_private_message")
async def edit_private_message(request: User_Schema.UpdateMessage, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.edit_message_private(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/edit_channel_message")
async def edit_message_channel(request: User_Schema.UpdateMessageChannel, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.edit_channel_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)

        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")
    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/edit_group_message")
async def edit_group_channel(request: User_Schema.UpdateMessageGroup, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.edit_group_message(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)

        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")
    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/create_group")
async def create_group(request: User_Schema.CreateGroup, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.create_group(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)

        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")
    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/create_channel")
async def create_channel(request: User_Schema.CreateChannel, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            response = await User_Services.create_channel(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)

        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")
    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)



@router.post("/update_channel_info")
async def update_channel_info(request: User_Schema.UpdateChannelInformation, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            respond = await User_Services.update_channel_info(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=respond)

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/left_channel")
async def left_channel(request: User_Schema.LeftChannel, collection: get_mongo_database = Depends(get_mongo_database)):
    try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            respond = await User_Services.left_channel(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=respond)
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")

    except BaseException as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)


@router.post("/left_group")
async def left_group(request: User_Schema.LeftGroup, collection: get_mongo_database = Depends(get_mongo_database)):
    # try:
        token_user = await JWT.decode_jwt(request.access_token)
        if token_user:
            respond = await User_Services.left_group(request, collection)
            return JSONResponse(status_code=status.HTTP_200_OK, content=respond)
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Token Expired")

    # except BaseException as error:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.args)




@router.post("/seen_message")
async def seen_message(token: dict, receiver: dict, collection: get_mongo_database = Depends(get_mongo_database)):
    sender = await Authjwt.JWT.decode_jwt(token["access_token"])
    unseen_messages = messages_serializer(collection[collection_dict["message_collection"]].find({"$and": [{"receiver": receiver["receiver"]},
                                                                    {"status": Status.SEND.value}, {"sender": sender}]}))
    if len(unseen_messages) > 0:
        update = collection[collection_dict["message_collection"]].update_many({
            "$and": [{"sender": sender}, {"receiver": receiver["receiver"]}, {"status": Status.SEND.value}]
        }, {
            "$set": {"status": Status.SEEN.value}
        })
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"number of seen message": f"{update.modified_count}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"unseen messages": {"Message": "nothing to seen"}})


@router.post("/rev_seen_message")
async def rev_seen_message(token: dict, receiver: dict, collection: get_mongo_database = Depends(get_mongo_database)):
    sender = await Authjwt.JWT.decode_jwt(token["access_token"])
    print(sender, receiver["receiver"], Status.SEND.value)
    unseen_messages = messages_serializer(collection[collection_dict["message_collection"]].find({"receiver": receiver["receiver"]}))
    if len(unseen_messages) > 0:
        update = collection[collection_dict["message_collection"]].update_many({
            "$and": [{"sender": sender}, {"receiver": receiver["receiver"]}, {"status": Status.SEEN.value}]
        }, {
            "$set": {"status": Status.SEND.value}
        })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"unseen messages": unseen_messages})


@router.post("/get_notification")
async def get_notification(token: dict, collection: get_mongo_database = Depends(get_mongo_database)):
    sender = await Authjwt.JWT.decode_jwt(token["access_token"])
    print(sender)
    notif_messages = messages_serializer(collection[collection_dict["message_collection"]].find({"$and": [{"sender": sender}, {"status": Status.SEND.value}]}))
    return JSONResponse(status_code=status.HTTP_200_OK, content=notif_messages)


@router.post("/search_CG")
async def search_CG(token: dict, search: dict, collection: get_mongo_database = Depends(get_mongo_database)):
    searched_item = cgs_serializer(collection[collection_dict[collection_dict["CG_Collection"]]].find({"$and": [{"name": search["search"]}, {"type": search["type"]}]}))
    # return await User_Services.get_channels_and_groups(user_ids["ids"], collection)
    if len(searched_item) > 0:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=searched_item)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                        content="Nothing Found(C/G) !!!!!!!")


@router.post("/get_cg_information")
async def get_info(token: dict, cg_id: dict, collection: get_mongo_database = Depends((get_mongo_database))):
    user_token = await Authjwt.JWT.decode_jwt(token["access_token"])
    if user_token:
        info = await User_Services.get_cg_info(objectID=cg_id["id"], type=cg_id["type"], database=collection)
        return JSONResponse(status_code=status.HTTP_200_OK, content=info)


# git init
# git add --all (or some other files)
# git commit -m "comment for this commit "
# git branch -M main(branch name )
# git remote add origin(remote name) https://github.com/edrez108/Telegram-test.git
# git push -u origin main
