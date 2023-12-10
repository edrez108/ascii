from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from pymongo import MongoClient
from fastapi import Depends
from bson import ObjectId
import os, binascii
from message.Schema import message_serializer, messages_serializer
DATABASE_USERNAME = "postgres"
DATABASE_PASSWORD = "admin"
DATABASE_HOST = "localhost"
DATABASE_NAME = "TelegramDatabase.db"
MONGODB_DATABASE_URL = "mongodb://localhost:27017"
DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

collection_dict = {
    "private_message_collection": "Messages Collection",
    "channel_collection": "Channels Collection",
    "group_collection": "Groups Collection",
    "group_message_collection": "Group Message Collection",
    "channel_message_collection": "Channel Message Collection",
    "image_collection": "Images Collection",
    "voice_collection": "Voices Collection",
    "video_collection": "Videos Collection",
    "file_collection": "Files Collection",
    "accounts_collection": "Account Collection"
}

types = {
    "Account Collection": {
        "name": "reza",
        "last_name": "eslami",
        "profile_image_addr": "address",
        "username": "reza eslami",
        "bio": "Add a few words about yourself",
        "phone_number": "09120000000",
        "blocked_users": ["user1"],
        "blocked_channels": ["channel1"],
        "blocked_groups": ["group1"]

    },
    "Messages Collection": {
        "name": "example name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",

            "title": "title",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "text": "some text ",
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]},

    "Channel Message Collection": {
        "name": "example Channel Message name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
            "title": "title Channel Message Collection",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "text": "some text ",
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]
    },

    "Group Message Collection": {
        "name": "example Group Message Collection name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
            "title": "title Group Message Collection",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "text": "some text ",
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]
    },


    # "Message_Private_Collection": {
    #     "name": "example name",
    #     "messages": [{
    #         "title": "title",
    #         "sender": "sender",
    #         "receiver": "receiver",
    #         "status": 1,
    #         "text": "some text ",
    #         "sending_time": "2020-10-15 23:59:59",
    #         "deleted_by_owner": False,
    #         "extera": [{"like": None}, {"smile": None}]
    #     }]
    # },

    "Channels Collection": {
        "name": "example Channel name",
        "information": {
            "description": "description",
            "subscription": 1,
            "profile_image": "URL of image",
            },
        "members": ["member1", "member2"],
        "admins": ["member1"]
        # ,
        # "add_left_dates": [{"member1": {"date_added": "2020-10-15 11:50", "date_left": ""}},
        #                    {"member2": {"date_added": "2022-12-12 22:60", "date_left": ""}}]
    },

    "Groups Collection": {
        "name": "example Group name",
        "information": {
            "description": "description",
            "subscription": 1,
            "profile_image": "URL of image",


        },
        "members": ["member1", "member2"],
        "admins": ["member1"],
        "add_left_dates": [{"member1": {"date_added": "2020-10-15 11:50", "date_left": ""}},
                           {"member2": {"date_added": "2022-12-12 22:60", "date_left": ""}}]
    },

    "Images Collection": {
            "name": "example media image name",
            "messages": [{
                "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
                "title": "example image title",
                "text": "some text about image",
                "image_url": "url",  # need size and preview in media collection
                "image_size": "1125",
                "image_preview": "nothing",
                "sender": "sender",
                "receiver": "receiver",
                "status": 1,
                "send_at": "2020-10-15 23:59:59",
                "deleted_by_owner": False,
                "seen_number": 0,
                "extera": [{"like": None}, {"smile": None}]
            }]

        },

    "Voices Collection": {
        "name": "example media voice name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
            "title": "example voice title",
            "text": "some text about voice",
            "voice_url": "url",  # need size and length in media collection
            "voice_size": "1125",
            "voice_length": "2:25",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]

    },

    "Videos Collection": {
        "name": "example media video name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
            "title": "example video title",
            "text": "some text about video",
            "video_url": "url",  # need size and preview and length in media collection
            "video_size": "1125",
            "video_length": "2:25",
            "video_preview": "nothing",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]

    },

    "Files Collection": {
        "name": "example media file name",
        "messages": [{
            "message_id": f"{ObjectId(str(binascii.b2a_hex(os.urandom(12)))[2:26])}",
            "title": "example file title",
            "file_url": "url",  # need size  in media collection
            "file_size": "1125",
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "send_at": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "seen_number": 0,
            "extera": [{"like": None}, {"smile": None}]
        }]
    },

    "Pointers Collection": {
        "dynamic address": "example address"
    }

}

engine = create_engine(DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)
    print("Database Created")
else:
    print("Database Exist")

local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
client = MongoClient(MONGODB_DATABASE_URL)


def get_database():
    db = local_session()
    try:
        yield db
    finally:
        db.close()


def get_mongo_db(db_name):

    if db_name in client.list_database_names():
        print("database already created !!")
        return client[f"{db_name}"]
    print("creating database .........")
    return client[f"{db_name}"]


def get_mongo_database():
    coll = client["TelegramMessage"]
    yield coll


def init_collection(database):
    coll_names = database.list_collection_names()

    for coll_name in collection_dict:
        if collection_dict[coll_name] not in coll_names:
            new_coll = database[f"{collection_dict[coll_name]}"]
            new_coll.insert_one(dict(types[collection_dict[coll_name]]))
            print(f"      Creating => {collection_dict[coll_name]} and Initialized")
        else:
            print(f"     {collection_dict[coll_name]} is exist ")
            if database[f"{collection_dict[coll_name]}"].find_one() is None:
                database[f"{collection_dict[coll_name]}"].insert_one(dict(types[collection_dict[coll_name]]))
                print(f"      Collection Exist => {collection_dict[coll_name]} so Initialized")
            else:
                print(f"     {collection_dict[coll_name]} Already Initialized")


init_collection(client["TelegramMessage"])

