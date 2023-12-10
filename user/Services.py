import datetime
from typing import List
from pymongo import InsertOne, UpdateOne
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from message import Models as Messages_Schema
from sqlalchemy.orm import Session
import user.Models as User_Models
import user.Schema as User_Schema
import message.Schema as Message_Schema
from Authjwt import JWT
from Database import collection_dict, get_mongo_database
from enum import Enum
from Authjwt import JWT
import os, binascii


class Status(Enum):
    NOT_SEND = 1
    SEND = 2
    SEEN = 3


types = {
    "channel": "Channels Collection",
    "group": "Groups Collection"
}


async def create_user(request: User_Models.User, database: Session):
    new_user = User_Models.User(phone_number=request.phone_number, password=await JWT.password_hasher(request.password))
    database.add(new_user)
    database.commit()
    database.refresh(new_user)
    return new_user


async def get_users(database: Session):
    return database.query(User_Models.User).all()



async def delete_user(phone_number, database: Session):
    database.query(User_Models.User).filter_by(phone_number=phone_number).delete()
    database.commit()
    return f"User with number {phone_number} Deleted"


#  get message endpoints
async def mongo_query_find(message_object_id: str, collection_name: str, database):
    return database.collection_name.aggregate([{"$match": {"_id": ObjectId(message_object_id)}},
                                                {"$unwind": "$messages"},
                                                {"$match": {"$and": [{"messages.status": 2},
                                                                     {"messages.deleted_by_owner": False}]}},
                                                {"$group": {"_id": "$_id", "name": {"$first": "$name"},
                                                            "messages": {"$push": "$messages"}}}])


async def mongo_query_find_channels_groups(message_object_id: str, collection_name, database):
    return database.collection[collection_name].find({"_id": ObjectId(message_object_id)})


async def get_messages(ids: dict, database):
    text_messages = await mongo_query_find(ids["message_collection_id"], collection_dict["message_collection"],
                                           database)
    image_messages = await mongo_query_find(ids["image_collection_id"], collection_dict["image_collection"], database)
    voice_messages = await mongo_query_find(ids["voice_collection_id"], collection_dict["voice_collection"], database)
    video_messages = await mongo_query_find(ids["video_collection_id"], collection_dict["video_collection"], database)
    file_messages = await mongo_query_find(ids["file_collection_id"], collection_dict["file_collection"], database)
    channel_messages = await mongo_query_find(ids["channel_collection_id"],
                                              collection_dict["channel_message_collection"], database)
    group_messages = await mongo_query_find(ids["group_collection_id"], collection_dict["group_message_collection"],
                                            database)
    deserialized_messages = await Message_Schema.messages_serializer(text_messages)
    deserialized_images = await Message_Schema.images_serializer(image_messages)
    deserialized_voices = await Message_Schema.voices_serializer(voice_messages)
    deserialized_videos = await Message_Schema.videos_serializer(video_messages)
    deserialized_files = await Message_Schema.files_serializer(file_messages)
    deserialized_channel = await Message_Schema.messages_serializer(channel_messages)
    deserialized_groups = await Message_Schema.messages_serializer(group_messages)
    return {"text Messages": deserialized_messages,
            "image Messages": deserialized_images,
            "voice Messages": deserialized_voices,
            "video Messages": deserialized_videos,
            "file Messages": deserialized_files,
            "channel Messages": deserialized_channel,
            "group Messages": deserialized_groups

            }


async def get_channels_and_groups(ids: dict, database):
    channels = await mongo_query_find_channels_groups(ids["channel_collection_id"],
                                                      collection_dict["channel_collection"], database)
    groups = await mongo_query_find_channels_groups(ids["group_collection_id"], collection_dict["group_collection"],
                                                    database)
    deserialized_channels = await Message_Schema.cgs_serializer(channels)
    deserialized_groups = await Message_Schema.cgs_serializer(groups)
    return {"channels info": deserialized_channels,
            "groups info": deserialized_groups}


# ######################################################################################################################
# last seen


async def create_account(request, collection):
    content = request
    content = dict(content)
    del content["access_token"]

    insert_to_account_collection = collection[collection_dict["accounts_collection"]].insert_one(content)
    return insert_to_account_collection.inserted_id


async def change_password():
    pass


async def delete_account(id: str,  collection):
    for collection_name in collection_dict:
        collection[collection_dict[collection_name]].delete_one({"_id": ObjectId(id)})

    print("successfully deleted")


async def update_last_seen(request: User_Schema.ChangeUserName, collection):
    update_result = collection[collection_dict["accounts_collection"]].update_one({"_id": ObjectId(request.id)},
                                                                                  {"$set": {
                                                                                      "name": request.new_first_name,
                                                                                      "last_name": request.new_last_name}})
    print(update_result.modified_count)
    if update_result.modified_count == 1:
        return JSONResponse(status_code=status.HTTP_200_OK, content=f"names updated !!!!!!!")
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nothing Changed")


async def add_blocked(request: User_Schema.BlockedUser, collection):
    list_of_blocked = collection[collection_dict["accounts_collection"]].find({"_id": ObjectId(request.id)})
    list_of_blocked = await Message_Schema.users_info_serializer(list_of_blocked)
    list_of_blocked = list_of_blocked[0].get("blocked_users")
    print(list_of_blocked, type(list_of_blocked))
    if request.new_blocked_user not in list_of_blocked:
        print("sadadaddasd")
        print(list_of_blocked)
        update_result = collection[collection_dict["accounts_collection"]].update_one({"_id": ObjectId(request.id)},
                                                                                      {"$push": {
                                                                                          "blocked_users": request.new_blocked_user}})
        print(update_result.matched_count)
        if update_result.matched_count == 1:
            return JSONResponse(status_code=status.HTTP_200_OK, content="One Blocked user insert")
    else:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="blocked user exist")
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="something went wrong in query ")


# ######################################################################################################################
# Send Messages (Private  ,  Channel  , Group  )  3h


async def send_private_message(request: User_Schema.SendTextMessage, collection):
    content = request
    content.send_at = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
    content.extera = []
    content = dict(content)
    send_to = content["send_to"]
    del content["send_to"]
    del content["access_token"]

    response = collection[collection_dict[send_to]].update_one({"_id": ObjectId(request.sender_id)},
                                                               {"$push": {"messages": content}},
                                                               upsert=True, )

    response2 = collection[collection_dict[send_to]].update_one({"_id": ObjectId(request.receiver_id)},
                                                                {"$push": {"messages": content}},
                                                                upsert=True, )

    return {"Modified_Count": {"sender": response.modified_count, "receiver": response2.modified_count},
            "UpSerted_id": {"sender": response.upserted_id, "receiver": response2.upserted_id}}


async def broadcast(message_id: str, sub_ids: list, content: str, collection):
    broadcast_requests_list = []

    for ids in sub_ids:
        broadcast_requests_list.append(UpdateOne({"_id": ObjectId(ids), "messages.message_id": ObjectId(message_id)},
                                                 {"$set": {"messages.$.text": content}}, upsert=True))

    return collection[collection_dict["private_message_collection"]].bulk_write(broadcast_requests_list, ordered=False)



async def send_channel_message(request: User_Schema.SendTextMessage, collection):
    content = request
    content.send_at = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
    content.extera = []
    content = dict(content)
    send_to = content["send_to"]
    del content["send_to"]
    del content["access_token"]

    collection[collection_dict["channel_message_collection"]].update_one({"_id": ObjectId(request.receiver_id)},
                                                    {"$push": {"messages": content}},
                                                    upsert=True)

    users_ids = collection[collection_dict["channel_collection"]].find_one({"_id": ObjectId(request.receiver_id)},
                                                                           {"information": 1})
    users_ids_list = await Message_Schema.users_ids_serializer(users_ids)
    await broadcast(users_ids_list, content, collection)
    return "Message BroadCast"


async def send_group_message(request: User_Schema.SendTextMessage, collection):
    pass
# async def send_image_message(request: User_Schema.SendImageMessage, collection):
#     content = requestq
#     content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
#     content = dict(content)
#     del content["access_token"]
#     del content["send_to"]
#     content["send_at"] = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
#     response = collection[collection_dict[request.send_to]].update_one({"_id": ObjectId(request.sender_id)},
#                                                                        {"$push": {"messages": content}},
#                                                                        upsert=True)
#
#     return {"Modified_Count": response.modified_count, "UpSerted_id": response.upserted_id}
#
#
# async def send_voice_message(request: User_Schema.SendVoiceMessage, collection):
#     content = request
#     content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
#     content = dict(content)
#     del content["access_token"]
#     del content["send_to"]
#     content["send_at"] = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
#     response = collection[collection_dict[request.send_to]].update_one({"_id": ObjectId(request.sender_id)},
#                                                                        {"$push": {"messages": content}},
#                                                                        upsert=True)
#     return {"Modified_Count": response.modified_count, "UpSerted_id": response.upserted_id}
#
#
#
# async def send_video_message(request: User_Schema.SendVideoMessage, collection):
#     content = request
#     content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
#     content = dict(content)
#     del content["access_token"]
#     del content["send_to"]
#     content["send_at"] = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
#     response = collection[collection_dict[request.send_to]].update_one({"_id": ObjectId(request.sender_id)},
#                                                                        {"$push": {"messages": content}},
#                                                                        upsert=True)
#     return {"Modified_Count": response.modified_count, "UpSerted_id": response.upserted_id}
#
#
# async def send_file_message(request: User_Schema.SendFileMessage, collection):
#     content = request
#     content.message_id = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
#     content = dict(content)
#     del content["access_token"]
#     del content["send_to"]
#     content["send_at"] = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
#     response = collection[collection_dict[request.send_to]].update_one({"_id": ObjectId(request.sender_id)},
#                                                                        {"$push": {"messages": content}},
#                                                                        upsert=True)
#     return {"Modified_Count": response.modified_count, "UpSerted_id": response.upserted_id}


# Forward Messages ( Private ,  Group  , Channel  ) 3h


#  can use send messages froms


# Delete Message ( for Owner ,  for every one ,in Private  ,  in Channel  , in Groupe) 3.5h

# ######################################################################################################################
async def delete_for_owner(request: User_Schema.DeleteOwnerMessage, collection):
    response = collection[collection_dict[request.delete_from]].update_one({"$and": [{"_id": ObjectId(request.user_id)},
                                                                                     {"messages.message_id": ObjectId(
                                                                                         request.message_id)},
                                                                                     {
                                                                                         "messages.deleted_by_owner": False}]},
                                                                           {"$set": {
                                                                               "messages.$.deleted_by_owner": True}})

    return {"modified_count": response.modified_count, "item_id": response.upserted_id}


async def delete_private_message(request: User_Schema.DeletePrivateMessage, collection):
    #  for a big collection maybe be better  to find two document base on Object id and then delete message from Messages
    result = collection[collection_dict["private_message_collection"]].update_many({},
                                                                                   {"$pull": {"messages": {"message_id": ObjectId(request.message_id)}}})
    return result.modified_count


async def delete_channel_message(request: User_Schema.DeletePrivateMessage, collection):
    token_user = await JWT.decode_jwt(request.access_token)
    admins = collection[collection_dict["channel_collection"]].find_one({"_id": ObjectId(request.receiver_id)}, {"information": 1})
    # print("\n\n\n\n\n\n\n\n\n", admins[0], "\n\n\n\n\n\n")
    admins = await Message_Schema.admins_ids_serializer(admins)
    if token_user:
        if request.sender_id in admins:

            # delete message from channel collection
            channel_result = collection[collection_dict["channel_message_collection"]].update_one({"_id": ObjectId(request.receiver_id)},
                                                                         {"$pull": {"messages": {"message_id": ObjectId(request.message_id)}}})

            # delete message from all members collection

            result = collection[collection_dict["private_message_collection"]].update_many({},
                                                                                  {"$pull": {"messages": {"message_id": ObjectId(request.message_id)}}})
            return {"many": result.modified_count, "single": channel_result.modified_count}



async def delete_group_message(request: User_Schema.DeletePrivateMessage, collection):

    admins = collection[collection_dict["channel_collection"]].find({"_id": ObjectId(request.receiver_id)},
                                                                    {"information": 1})
    admins = await Message_Schema.admins_serializer(admins)
    if request.sender_id in admins:

        # delete message from channel collection
        collection[collection_dict["channel_collection"]].update_one({"_id": ObjectId(request.message_id)},
                                                                     {"$pull": {"messages": {
                                                                         "message_id": ObjectId(request.message_id)}}})

        # delete message from all members collection

        result = collection[collection_dict["private_message_collection"]].update_many({},
                                                                                       {"$pull": {"messages": {
                                                                                           "message_id": ObjectId(
                                                                                               request.message_id)}}})
        return result.modified_count



async def delete_messages(user_id, message_ids: list, collection):

    request_list = []
    for message_id in message_ids:
        request_list.append(UpdateOne({"_id": ObjectId(user_id)}, {"$pull": {"messages": {"message_id": message_id}}}))

    bulk_result = collection[collection_dict["private_message_collection"]].bulk_write(request_list, ordered=False)
    return bulk_result

# ######################################################################################################################



# Edit(update) Message (in Private , in Channel  , in Group  ) 3h



async def edit_message_private(request: User_Schema.UpdateMessage, collection):


    request_list = [
         UpdateOne({"_id": ObjectId(request.sender_id), "messages.message_id": ObjectId(request.message_id)}, {"$set": {"messages.$.text": request.new_text}}),
         UpdateOne({"_id": ObjectId(request.receiver_id), "messages.message_id": ObjectId(request.message_id)}, {"$set": {"messages.$.text": request.new_text}})
     ]

    bulk_result = collection[collection_dict["private_message_collection"]].bulk_write(request_list)


    print(bulk_result.matched_count, bulk_result.modified_count)
    return True



async def edit_channel_message(request: User_Schema.UpdateMessageChannel, collection):

    list_general_requests = []
#   query for editing message for admin

    admins_sub_list = collection[collection_dict["channel_collection"]].find_one({"_id": ObjectId(request.channel_id)}, {"information": 1})
    if admins_sub_list is not None:
        admins_sub_list = await Message_Schema.admins_sub_serializer(admins_sub_list)
        if request.sender_id in admins_sub_list["list_sub_ids"]:
            # edit message in channel collection
            collection[collection_dict["channel_message_collection"]].update_one({"_id": ObjectId(request.channel_id), "messages.message_id": ObjectId(request.message_id)},
                                  {"$set": {"messages.$.text": request.new_text}})
            # edit message for admin in message collection
            collection[collection_dict["private_message_collection"]].update_one({"_id": ObjectId(request.sender_id), "messages.message_id": ObjectId(request.message_id)},
                                  {"$set": {"messages.$.text": request.new_text}})

            # broadcast edit for all subs
            response = await broadcast(request.message_id, admins_sub_list["list_sub_ids"], request.new_text, collection)
            return f"Sent for {response.matched_count}"

        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="not an admin")
    else:
        JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Channel Not Fount (channel_id Is wrong")


async def edit_group_message(request: User_Schema.UpdateMessageGroup, collection):
    list_general_requests = []
    #   fetching group information
    admins_sub_list = collection[collection_dict["group_collection"]].find_one({"_id": ObjectId(request.group_id)},
                                                                               {"information": 1})
    if admins_sub_list is not None:
        admins_sub_list = await Message_Schema.admins_sub_serializer(admins_sub_list)
        # edit message in group message collection
        collection[collection_dict["group_message_collection"]].update_one(
            {"_id": ObjectId(request.group_id), "messages.message_id": ObjectId(request.message_id)},
            {"$set": {"messages.$.text": request.new_text}})

        # # edit message for admin in message collection
        # collection[collection_dict["private_message_collection"]].update_one(
        #     {"_id": ObjectId(request.sender_id), "messages.message_id": ObjectId(request.message_id)},
        #     {"$set": {"messages.$.text": request.new_text}})

        # broadcast edit for all subs
        response = await broadcast(request.message_id, admins_sub_list["list_sub_ids"], request.new_text,
                                   collection)
        return f"Sent for {response.matched_count}"


    else:
        JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="group Not Fount (group Is wrong")

########################################################################################################################
#  Create (Channel  ,  Group  , new Grivate ) delete them 2h



async def create_private_chat(request: User_Schema.CreateChat, collection):
    pass
# it can be handel  in front-end



async def create_group(request: User_Schema.CreateGroup, collection):
    #   fetch created group names
    print("first")
    created_group_names_list = collection[collection_dict["group_collection"]].find_one({"name": request.name})

    print("second")
    if created_group_names_list is not None:
        return "NAME ALREADY EXIST"

    print("third")
    content = request
    content.created_at = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    del content.access_token
    content = dict(content)

    content["_id"] = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
    content["image_url"] = ""

    sub_admin_ids = [content["members"], content["admins"]]
    add_left_test = []
    for member_id in sub_admin_ids:
        add_left_test.append({"id": member_id[0],
                              "date_added": str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")),
                              "date_left": ""})

    content["add_left_dates"] = add_left_test
    print("fourth")
    insert_result_info = collection[collection_dict["group_collection"]].insert_one(dict(content))
    print("fifth")
    insert_result_message = collection[collection_dict["group_message_collection"]].insert_one({
        "_id": content["_id"],
        "messages": []
    })
    print("sixth", str(insert_result_info.inserted_id), str(insert_result_message.inserted_id))
    return {"insert result for group collection": str(insert_result_info.inserted_id), "insert result for group message collection": str(insert_result_message.inserted_id)}





async def create_channel(request: User_Schema.CreateChannel, collection):

    #   fetch created group names
    created_channel_names_list = collection[collection_dict["channel_collection"]].find_one({"name": request.name})

    if created_channel_names_list is not None:
        return "NAME ALREADY EXIST"

    content = request
    content.created_at = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    del content.access_token
    content = dict(content)

    content["_id"] = ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])
    content["image_url"] = ""

    insert_result_info = collection[collection_dict["channel_collection"]].insert_one(dict(content))

    insert_result_message = collection[collection_dict["channel_message_collection"]].insert_one({
        "_id": content["_id"],
        "messages": []
    })
    print("sixth", str(insert_result_info.inserted_id), str(insert_result_message.inserted_id))
    return {"insert result for channel collection": str(insert_result_info.inserted_id), "insert result for channel message collection": str(insert_result_message.inserted_id)}



########################################################################################################################
# update profile for (Channel , Group ) change information and add admin 2h



async def update_channel_info(request: User_Schema.UpdateChannelInformation, collection):
    admins_ids_list = await Message_Schema.admins_serializer(collection[collection_dict["channel_collection"]].find_one({"_id": request.channel_id}, {"admins": 1}))
    if request.sender_id in admins_ids_list:
        result = collection[collection_dict["channel_collection"]].update_one({"_id": request.channel_id},
                                                                              {"$set": {
                                                                                  "name": request.name,
                                                                                  "image_url": request.image_url,
                                                                                  "description": request.description,
                                                                                  "channel_type": request.channel_type,
                                                                                  "public_link": request.public_link
                                                                                  }})
        return result.matched_count



async def update_group_info(request: User_Schema.UpdateChannelInformation, collection):
    admins_ids_list = await Message_Schema.admins_serializer(
        collection[collection_dict["group_collection"]].find_one({"_id": request.channel_id}, {"admins": 1}))
    if request.sender_id in admins_ids_list:
        result = collection[collection_dict["group_collection"]].update_one({"_id": request.channel_id},
                                                                              {"$set": {
                                                                                  "name": request.name,
                                                                                  "image_url": request.image_url,
                                                                                  "description": request.description,
                                                                                  "channel_type": request.channel_type,
                                                                                  "public_link": request.public_link
                                                                              }})
        return result.matched_count





########################################################################################################################
# left the group and left the channel  and 2h add to group and channel



async def left_group(request: User_Schema.LeftGroup, collection):

    collection[collection_dict["group_collection"]].update_one(
                                                    {"_id": ObjectId(request.group_id)}, {"$pull": {"members": request.user_id, "admins": request.user_id}})

    collection[collection_dict["group_collection"]].update_one({"_id": ObjectId(request.group_id)},
                                                     {"$set":
                                                          {"add_left_dates.$[x].date_left": str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))}},
                                                     array_filters=[{"x.id": request.user_id}],
                                                     upsert=True)


    message_ids_list = collection[collection_dict["group_message_collection"]].aggregate([
                                                                {"$match": {"_id": ObjectId(request.group_id)}},
                                                                {"$unwind": "$messages"},
                                                                {"$group": {"_id": "$_id",
                                                                            "messages_id": {"$push": "$messages.message_id"}}}
    ])
    message_ids_list = await Message_Schema.group_ids_serializer(message_ids_list)
    print(message_ids_list)
    #   delete messages from user message collection
    message_result = await delete_messages(request.user_id, message_ids_list, collection)
    return message_result.matched_count


async def left_channel(request: User_Schema.LeftChannel, collection):
    collection[collection_dict["channel_collection"]].update_one(
        {"_id": ObjectId(request.channel_id)}, {"$pull": {"members": request.user_id, "admins": request.user_id}})

    collection[collection_dict["channel_collection"]].update_one({"_id": ObjectId(request.group_id)},
                                                               {"$set":
                                                                    {"add_left_dates.$[x].date_left": str(
                                                                        datetime.datetime.now().strftime(
                                                                            "%y-%m-%d %H:%M:%S"))}},
                                                               array_filters=[{"x.id": request.user_id}],
                                                               upsert=True)

    message_ids_list = collection[collection_dict["channel_message_collection"]].aggregate([
        {"$match": {"_id": ObjectId(request.group_id)}},
        {"$unwind": "$messages"},
        {"$group": {"_id": "$_id",
                    "messages_id": {"$push": "$messages.message_id"}}}
    ])
    message_ids_list = await Message_Schema.group_ids_serializer(message_ids_list)
    #   delete messages from user message collection
    message_result = await delete_messages(request.user_id, message_ids_list, collection)
    return message_result.matched_count


async def delete_private_chat(request: User_Schema.DeletePrivateChat, collection):
    pass

########################################################################################################################
# workers (seen number updater ) 6 h


async def get_cg_info(objectID: str, type: str, database):
    return await Message_Schema.cgs_serializer(await mongo_query_find_channels_groups(objectID,
                                                                                      types[type], database))


