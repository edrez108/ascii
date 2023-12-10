async def message_serializer(message) -> dict:
    mess = list(message["messages"])
    message_list = []
    for me in mess:
        message_list.append({

                "title": me["title"],
                "text": me["text"],
                "sender": me["sender"],
                "receiver": me["receiver"],
                "status": me["status"],
                "sending_time": me["sending_time"],
                "deleted_by_owner": me["deleted_by_owner"],
                "seen_number": str(me["seen_number"]),
                "extera": list(me["extera"])
        })
    return {
        "_id": str(message["_id"]),
        "name": message["name"],
        "messages": message_list
    }


async def messages_serializer(messages) -> list:
    return [await message_serializer(message) for message in messages]


async def group_name_serializer(group):
    return {
        "name": group["name"]
    }


async def group_names_serializer(groups) -> list:
    return [await group_name_serializer(group) for group in groups]


async def cg_serializer(cg):
    if "add_left_dates" not in cg.keys():
        return {
            "_id": str(cg["_id"]),
            "name": cg["name"],
            "information": dict(cg["information"]),
        }
    return {
        "_id": str(cg["_id"]),
        "name": cg["name"],
        "information": dict(cg["information"]),
        "add_left_dates": list(cg["add_left_dates"])
    }


async def cgs_serializer(cgs):
    return [await cg_serializer(cg) for cg in cgs]


async def image_serializer(image):
    return {
        "_id": str(image["_id"]),
        "messages": list(image["messages"]),
    }


async def images_serializer(images):
    return [await image_serializer(image) for image in images]


async def voice_serializer(voice):
    return {
        "_id": str(voice["_id"]),
        "name": voice["name"],
        "messages": list(voice["messages"])
        # "title": voice["title"],
        # "voice_url": voice["voice_url"],
        # "voice_size": voice["voice_size"],
        # "voice_length": voice["voice_length"],
        # "sender": voice["sender"],
        # "receiver": voice["receiver"],
        # "status": voice["status"],
        # "sending_time": voice["sending_time"],
        # "deleted_by_owner": voice["deleted_by_owner"],
        # "seen_number": voice["seen_number"],
        # "extera": list(voice["extera"])
    }


async def voices_serializer(voices):
    return [await voice_serializer(voice) for voice in voices]


async def video_serializer(video):
    return {
        "_id": str(video["_id"]),
        "name": video["name"],
        "messages": list(video["messages"])
        # "title": video["title"],
        # "video_url": video["video_url"],
        # "video_size": video["video_size"],
        # "video_length": video["video_length"],
        # "video_preview": video["video_preview"],
        # "sender": video["sender"],
        # "receiver": video["receiver"],
        # "status": video["status"],
        # "sending_time": video["sending_time"],
        # "deleted_by_owner": video["deleted_by_owner"],
        # "seen_number": video["seen_number"],
        # "extera": list(video["extera"])
    }


async def videos_serializer(videos):
    return [await voice_serializer(video) for video in videos]


async def file_serializer(file):
    return {
        "_id": str(file["_id"]),
        "name": file["name"],
        "messages": list(file["messages"])
        # "title": file["title"],
        # "file_url": file["file_url"],
        # "file_size": file["file_size"],
        # "sender": file["sender"],
        # "receiver": file["receiver"],
        # "status": file["status"],
        # "sending_time": file["sending_time"],
        # "deleted_by_owner": file["deleted_by_owner"],
        # "seen_number": file["seen_number"],
        # "extera": list(file["extera"])
    }


async def files_serializer(files):
    return [await file_serializer(file) for file in files]


async def user_info_serializer(info):
    return {
        "_id": str(info["_id"]),
        "name": info["name"],
        "last_name": info["last_name"],
        "profile_image_addr": info["profile_image_addr"],
        "username": info["username"],
        "bio": info["bio"],
        "phone_number": info["phone_number"],
        "blocked_users": list(info["blocked_users"]),
        "blocked_channels": list(info["blocked_channels"]),
        "blocked_groups": list(info["blocked_groups"])

    }


async def users_info_serializer(infos):
    return [await user_info_serializer(info) for info in infos]


async def admins_sub_serializer(info):
    list_sub_ids = info["members"]
    list_admin_ids = info["admins"]
    return {
        "list_sub_ids": list_sub_ids,
        "list_admin_ids": list_admin_ids
    }


async def admins_serializer(info):
    return list(info["admins"])



async def sub_serializer(info):
    return list(info["members"])




async def group_ids_serializer(idps):
    # return [await group_id_serializer(idp) for idp in idps]
    for i in idps:
        return i["messages_id"]


async def _serializer(idps):
    # return [await group_id_serializer(idp) for idp in idps]
    for i in idps:
        return i["match"]