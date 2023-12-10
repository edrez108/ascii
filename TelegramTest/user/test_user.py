import random
from faker import Faker
import pytest
import requests
import json
import user.Schema as User_Schema
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import AsyncIterator
import httpx
import pytest_asyncio
from Database import collection_dict, types
import jwt
from main import app
import time
from decouple import config
from passlib.context import CryptContext
Base_ENDPOINT = "http://127.0.0.1:8000/user"
End_Point = {
    "index": Base_ENDPOINT+"/",
    "create_user": Base_ENDPOINT+"/signup",
    "login": Base_ENDPOINT+"/login",
    "delete_user": Base_ENDPOINT+"/delete_user",
    "get_all_users": Base_ENDPOINT+"/get_all_users",
    "create_account": Base_ENDPOINT+"/create_account",
    "change_password": Base_ENDPOINT+"/change_password",
    "delete_account": Base_ENDPOINT+"/delete_account",
    "update_last_seen": Base_ENDPOINT+"/update_last_seen",
    "update_user_first_last_name": Base_ENDPOINT+"/change_name",
    "add_blocked_user_channel_group": Base_ENDPOINT+"/add_blocked",
    "send_private_message": Base_ENDPOINT+"/send_private_message",
    "send_channel_message": Base_ENDPOINT+"/send_channel_message",
    "delete-owner_message": Base_ENDPOINT+"/delete_owner_message",
    "delete_private_message": Base_ENDPOINT+"/delete_private_message",
    "delete_channel_message": Base_ENDPOINT+"/delete_channel_message",
    "delete_group_message": Base_ENDPOINT+"/delete_group_message",
    "edit_private_message": Base_ENDPOINT+"/edit_private_message",
    "edit_message_channel": Base_ENDPOINT+"/edit_channel_message",
    "edit_group_message": Base_ENDPOINT+"/edit_group_message",
    "create_group": Base_ENDPOINT+"/create_group",
    "create_channel": Base_ENDPOINT+"/create_channel",
    "update_channel_info": Base_ENDPOINT+"/update_channel_info",
    "left_channel": Base_ENDPOINT+"/left_channel",
    "left_group": Base_ENDPOINT+"/left_group",
    "seen_message": Base_ENDPOINT+"/seen_message",


}
fake = Faker(locale="en-US")
print(fake.name())


class Generator:
    @staticmethod
    def phone_number():
        return "09121111" + str(random.randint(100, 999))

    @staticmethod
    def password():
        return "11235813"


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

hasher = CryptContext(schemes=["sha256_crypt", "des_crypt"])

inputs = {
        "phone_number": "09120000000",
        "password": "11235813"
    }


async def decode_jwt(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        return decode_token['phone_number'] if decode_token['expiry'] >= time.time() else None
    except:
        return None


async def token_generator(inputs , client):
    response = client.post(End_Point["login"], json=inputs)
    assert response.status_code == 200
    data = response.json()
    return data


async def create_user(inputs, client):

    response = client.post(End_Point["create_user"], json=inputs)
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]
    assert data["phone_number"] == inputs["phone_number"]
    return data["phone_number"]


async def delete_user(inputs, phone_from_data, client):
    response_delete = client.post(End_Point["delete_user"],
                                  json=await token_generator(inputs, client))
    data_delete = response_delete.json()
    assert data_delete == f"User with number {phone_from_data} Deleted"



@pytest_asyncio.fixture()
async def client():
        client= TestClient(app=app)
        yield client



@pytest.mark.asyncio
async def test_token_generator(client):

    response = client.post(End_Point["login"], json=inputs)
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    assert len(token) > 10
    decoded_token = await decode_jwt(token)
    print(decoded_token)

    assert decoded_token == inputs["phone_number"]


@pytest.mark.asyncio
async def test_create_user(client):

    instance_input = {
        "phone_number": Generator.phone_number(),
        "password": Generator.password()
    }
    #
    phone_from_data = await create_user(instance_input, client)

    await delete_user(instance_input, phone_from_data, client)


@pytest.mark.asyncio
async def test_get_all_users(client):
    # instance_input = {
    #     "phone_number": Generator.phone_number(),
    #     "password": Generator.password()
    # }

    response = client.post(End_Point["get_all_users"], json=await token_generator(inputs,
                                                                                client))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_account(client):
    instance_input = {
        "access_token": await token_generator({
            "phone_number": Generator.phone_number(),
            "password": Generator.password()
        }, client),
        "name": fake.first_name(),
        "last_name": fake.last_name(),
        "profile_image_addr": fake.uri(),
        "username": fake.unique.name(),
        "bio": fake.text(),
        "phone_number": fake.phone_number,
        "blocked_users": [fake.unique.first_name(), fake.unique.first_name(), fake.unique.first_name()],
        "blocked_channels": [fake.unique.first_name(), fake.unique.first_name(), fake.unique.first_name()],
        "blocked_groups": [fake.unique.first_name()]
    }

    insert_response = client.post(End_Point["create_account"], json=instance_input)
    assert insert_response.status_code == 200
    data = insert_response.json()
    delete_instance_input = {
        "access_token": instance_input["access_token"],
        "id": data["id"]

    }
    delete_response = client.post(End_Point["delete_account"], json=delete_instance_input)
    assert delete_response.status_code == 200
    assert delete_response.json() == "successfully deleted"





