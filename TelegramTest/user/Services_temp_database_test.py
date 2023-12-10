import pytest
import user.Schema as User_Schema
import user.Models as User_Model
from Authjwt.JWT import verify_password
from mock import Mock
import Authjwt.JWT
import user.Services as User_Services
import asyncio
import TelegramTest.conf_test_db as test_db
from bson import ObjectId
import os, binascii


@pytest.mark.asyncio
@pytest.mark.parametrize("new_user,database", [({"phone_number": "09120000000",
                                                 "password": "11235813"},
                                                test_db.override_get_postgres_db())])
async def test_create_user(new_user, database):
    model = User_Model.User(new_user.get("phone_number"), new_user.get("password"))
    response = await User_Services.create_user(model, database)
    delete_response = database.query(User_Model.User).filter_by(phone_number=model.phone_number).delete()
    database.commit()
    assert delete_response == True, "deleted test item"


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
                                                test_db.override_get_postgres_db())])
async def test_get_users(new_user, database):
    # add all test users
    for user in new_user:
        model = User_Model.User(user.get("phone_number"), user.get("password"))
        database.add(model)
        database.commit()

    # get all test users
    fetched_users = database.query(User_Model.User)
    fetched_users = list(fetched_users)
    assert len(fetched_users) == len(new_user)
    for i, fetched_user in enumerate(fetched_users):
        if fetched_user.phone_number not in new_user.__getitem__(i).get("phone_number"):
            assert None

    # delete all test users
    delete_response = database.query(User_Model.User).delete()
    database.commit()
    assert delete_response != 0


@pytest.mark.asyncio
@pytest.mark.parametrize("new_user,database", [({"phone_number": "09120000000",
                                                 "password": "11235813"},
                                                test_db.override_get_postgres_db())])
async def test_delete_user(new_user, database):
    model = User_Model.User(new_user.get("phone_number"), new_user.get("password"))
    insert_res = database.add(model)
    database.commit()
    delete_res = await User_Services.delete_user(new_user.get("phone_number"), database)
    database.commit()
    assert insert_res != 0, "test user inserted"
    assert delete_res == f"User with number {new_user.get('phone_number')} Deleted", "deleting test user"


@pytest.mark.asyncio
@pytest.mark.parametrize("user_document_object_id,message_object_id,collection_name,database",
                         [(str(binascii.b2a_hex(os.urandom(12)))[2:26],
                          str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           "test_collection",
                           test_db.override_get_mongo_db())])
async def test_mongo_query_find(user_document_object_id, message_object_id, collection_name, database):

    # add new document in collection
    test_message_document = test_db.types.get("Messages Collection")
    test_message_document["_id"] = ObjectId(user_document_object_id)
    test_message_document["messages"][0]["message_id"] = ObjectId(message_object_id)
    test_message_document["messages"][0]["status"] = 2
    # add a test document in collection for testing querty find method
    insert_response = database.collection[collection_name].insert_one(test_message_document)
    assert insert_response.inserted_id == ObjectId(user_document_object_id), "inserted id"


    # find inserted test_message
    retrv_message = await User_Services.mongo_query_find(user_document_object_id, collection_name, database)
    for message in retrv_message:

        assert message["_id"] == ObjectId(user_document_object_id), "retrieved message"


    # delete test _message
    delete_test_messaeg_response = database.collection[collection_name].delete_one({"_id": ObjectId(user_document_object_id)})
    assert delete_test_messaeg_response.deleted_count == 1, "message deleted"


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_object_id,group_object_id,collection_name,database",
                         [(str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           str(binascii.b2a_hex(os.urandom(12)))[2:26],
                           "test_collection", test_db.override_get_mongo_db())])
async def test_mongo_query_find_channels_groups(channel_object_id, group_object_id: str, collection_name, database):
    # create group and channel
    test_group = test_db.types["Groups Collection"]
    test_group["_id"] = ObjectId(group_object_id)
    test_group["name"] = "tps344023"

    test_channel = test_db.types["Channels Collection"]
    test_channel["_id"] = ObjectId(channel_object_id)
    test_channel["name"] = "D-Link-s344023"




    # add group and channel to test collection
    database.collection[collection_name].insert_one(test_channel)
    database.collection[collection_name].insert_one(test_group)


    # test mongo_query_find_channels_groups

    find_group_response = await User_Services.mongo_query_find_channels_groups(group_object_id, collection_name, database)
    find_channel_response = await User_Services.mongo_query_find_channels_groups(channel_object_id, collection_name, database)
    assert find_channel_response[0]["_id"] == ObjectId(channel_object_id), "channel test"
    assert find_group_response[0]["_id"] == ObjectId(group_object_id), "group test"


    # delete test_channel and test_group
    database.collection[collection_name].delete_one({"_id": ObjectId(channel_object_id)})
    database.collection[collection_name].delete_one({"_id": ObjectId(group_object_id)})






















