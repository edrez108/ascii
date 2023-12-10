import pytest
import user.Schema as User_Schema
import user.Models as User_Models

import user.Validation as Validation
from TelegramTest.conf_test_db import override_get_mongo_db, override_get_postgres_db
from fastapi import Depends
from sqlalchemy.orm import Session
import Authjwt.JWT


@pytest.mark.asyncio
@pytest.mark.parametrize("phone_number, password", [("09120000000", "11235813")])
async def test_verify_existing_user(phone_number, password):

    new_user = User_Models.User(phone_number=phone_number, password=await Authjwt.JWT.password_hasher(password))
    database = override_get_postgres_db()
    database.add(new_user)
    database.commit()
    # database.refresh(new_user)
    response = await Validation.verify_existing_user(new_user.phone_number, override_get_postgres_db())
    print(response)

    assert response == True

    database.delete(new_user)
    database.commit()
