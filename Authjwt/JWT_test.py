import pytest
import Authjwt.JWT
import time
import jwt
from mock import Mock
from unittest.mock import patch
from Authjwt.order import Order

passs = "main_reason"


@pytest.fixture
@pytest.mark.asyncio
def password():
    return passs


@pytest.mark.asyncio
async def test_password_hasher(password):
    print(password)
    assert Authjwt.JWT.hasher.verify(password, await Authjwt.JWT.password_hasher(password))


@pytest.mark.asyncio
@pytest.mark.parametrize("pas", ["reza"])
async def test_verify_password(pas):




    assert await Authjwt.JWT.verify_password(pas, Authjwt.JWT.hasher.hash(pas))


@pytest.mark.asyncio
@pytest.mark.parametrize("phone_number", ["09120000000"])
async def test_token_response(phone_number):

        payload = {
            "phone_number": phone_number,
            "expiry": time.time() + 1800
        }
        token = jwt.encode(payload, Authjwt.JWT.JWT_SECRET, algorithm=Authjwt.JWT.JWT_ALGORITHM)
        assert await Authjwt.JWT.token_response(token) == {
            "access_token": token
        }


@pytest.mark.asyncio
@pytest.mark.parametrize("phone_number", ["09120000000"])
async def test_sign_jwt(phone_number):

        payload = {
            "phone_number": phone_number,
            "expiry": time.time() + 1800
        }
        token = jwt.encode(payload, Authjwt.JWT.JWT_SECRET, algorithm=Authjwt.JWT.JWT_ALGORITHM)
        assert await Authjwt.JWT.sign_jwt(phone_number) == {
            "access_token": token
        }


@pytest.mark.asyncio
@pytest.mark.parametrize("phone_number", ["09120000000"])
async def test_decode_jwt(phone_number):

        payload = {
            "phone_number": phone_number,
            "expiry": time.time() + 1800
        }
        token = jwt.encode(payload, Authjwt.JWT.JWT_SECRET, algorithm=Authjwt.JWT.JWT_ALGORITHM)
        assert await Authjwt.JWT.decode_jwt(token) == phone_number


@pytest.mark.asyncio
@patch('Authjwt.JWT.decode_jwt')
async def test_token_user(mock_get):
    mock_get.return_value = "khare_mannam"

    assert await Authjwt.JWT.decode_jwt() == "khare_mannam"


@pytest.mark.asyncio
async def test_order_is_filled():
    order = Order("mashroom", 20)
    warehouse = Mock()
    warehouse.has_inventory.return_value = True
    warehouse.remove.return_value = None

    order.fill(warehouse)

    assert not order.is_filled()
