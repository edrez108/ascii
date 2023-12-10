import pytest
import user.Schema as User_Schema
import user.Models as User_Models
from Authjwt.JWT import verify_password
from unittest.mock import Mock
from mock import patch
import Authjwt.JWT
import user.Services as User_Services
import asyncio
import os, binascii
from bson import ObjectId
import TelegramTest.conf_test_db as test_db


@pytest.mark.asyncio
@pytest.mark.parametrize("new_user,database", [(User_Models.User(phone_number="09120000000",
                                                                password=asyncio.run(Authjwt.JWT.password_hasher("11235813"))),
                                                Mock())])
async def test_create_user(new_user, database):
    database.add(new_user).return_value = True
    database.commit().return_value = True
    database.refresh(new_user).return_value = True

    response = await User_Services.create_user(new_user, database)
    assert response != None


@pytest.mark.asyncio
@pytest.mark.parametrize("new_user,database", [([{"phone_number": "09120000000",
                                                 "password": "11235813"},
                                                 {"phone_number": "09120000001",
                                                  "password": "11235813"},
                                                 {"phone_number": "09120000002",
                                                 "password": "11235813"},
                                                 {"phone_number": "09120000003",
                                                 "password": "11235813"}
                                                 ],
                                                Mock())])
async def test_get_users(new_user, database):
    database.query(User_Models.User).all.return_value = [{"phone_number": "09120000000",
                                                           "password": "11235813"},
                                                          {"phone_number": "09120000001",
                                                           "password": "11235813"},
                                                          {"phone_number": "09120000002",
                                                           "password": "11235813"},
                                                          {"phone_number": "09120000003",
                                                           "password": "11235813"}
                                                           ]
    response = await User_Services.get_users(database)
    for res in response:
        if res not in response:
            if res not in new_user:
                assert 1 == 0, "retrieved users is not equal to inserted users"


@pytest.mark.asyncio
@pytest.mark.parametrize("new_user,database", [("09120000000", Mock())])
async def test_delete_user(new_user, database):
    database.query(User_Models.User).filter_by(phone_number=new_user).delete.return_value = True
    database.commit().return_value = True

    response = await User_Services.delete_user(new_user, database)
    assert response == f"User with number {new_user} Deleted"


@pytest.mark.asyncio
@pytest.mark.parametrize("user_document_object_id,message_object_id,collection_name,database",
                         [(str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           "test_collection",
                           Mock())])
async def test_mongo_query_find(user_document_object_id, message_object_id, collection_name, database):

    # create test message
    test_message_document = test_db.types.get("Messages Collection")
    test_message_document["_id"] = ObjectId(user_document_object_id)
    test_message_document["messages"][0]["message_id"] = ObjectId(message_object_id)
    test_message_document["messages"][0]["status"] = 2

    # create Mock object for replace inserting to database
    database.collection_name.aggregate.return_value = dict(test_message_document)

    # find inserted test_message
    retrv_message = await User_Services.mongo_query_find(user_document_object_id, collection_name, database)


    assert retrv_message["_id"] == ObjectId(user_document_object_id), "retrieved message"


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_object_id,group_object_id,collection_name,database",
                         [(str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           Mock())])
async def test_mongo_query_find_channels_groups(channel_object_id, group_object_id: str, collection_name, database):
    # create group and channel
    database_group = database
    database_channel = database

    # database_channel.collection[collection_name].find.return_value =
    # database_group.collection[collection_name].find.return_value =

    # test_group = test_db.types["Groups Collection"]
    # test_group["_id"] = ObjectId(group_object_id)
    # test_group["name"] = "tps344023"
    #
    # test_channel = test_db.types["Channels Collection"]
    # test_channel["_id"] = ObjectId(channel_object_id)
    # test_channel["name"] = "D-Link-s344023"




    # add group and channel to test collection
    # database.collection[collection_name].insert_one(test_channel)
    # database.collection[collection_name].insert_one(test_group)


    # test mongo_query_find_channels_groups

    find_group_response = await User_Services.mongo_query_find_channels_groups(group_object_id, collection_name, database_group)
    find_channel_response = await User_Services.mongo_query_find_channels_groups(channel_object_id, collection_name, database)
    assert find_channel_response[0]["_id"] == ObjectId(channel_object_id), "channel test"
    assert find_group_response[0]["_id"] == ObjectId(group_object_id), "group test"


    # delete test_channel and test_group
    database.collection[collection_name].delete_one({"_id": ObjectId(channel_object_id)})
    database.collection[collection_name].delete_one({"_id": ObjectId(group_object_id)})




















