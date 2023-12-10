import pytest
import user.Schema as User_models
from Authjwt.JWT import verify_password
from mock import Mock
import user.Validation as Validation


@pytest.mark.asyncio
@pytest.mark.parametrize("phone_number", ["09120000000"])
async def test_verify_existing_user(phone_number):
    user_model = User_models.User
    user_model.phone_number = phone_number
    user_model.password = "hash(5)=?65198161561r423rrf1254rfe451fw5f4ERrg1f4r16f16ff3,l./"
    user_model.id = 5
    user_model.username = "Unknown"
    database_mock = Mock()
    database_mock.query(User_models.User).filter_by(phone_number=phone_number).first.return_value = user_model
    response = await Validation.verify_existing_user(phone_number, database_mock)

    assert response == True
