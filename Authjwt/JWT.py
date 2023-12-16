# This JWT  file is a JWT handler ,and it is responsible for signing encoding decoding
#and returning JWTs.
from fastapi import HTTPException, status
import time
import jwt
from decouple import config
from jose import JWTError


from passlib.context import CryptContext

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

hasher = CryptContext(schemes=["sha256_crypt", "des_crypt"])


async def password_hasher(password):
    return hasher.hash(password)


async def verify_password(plain_pass, hashed_pass):
    return hasher.verify(plain_pass, hashed_pass)


async def token_response(token: str):
    return {
        "access_token": token
    }

# salam khodeto in modele for your in my heart
async def sign_jwt(phone_number: str):
    try:
        payload = {
            "phone_number": phone_number,
            "expiry": time.time() + 1800
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return await token_response(token)
    except:
        HTTPException(status_code=status.HTTP_409_CONFLICT)


async def decode_jwt(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        return decode_token['phone_number'] if decode_token['expiry'] >= time.time() else None
    except:
        return None



# git init
# git add --all (or some other files)
# git commit -m "comment for this commit "
# git branch -M main(branch name )
# git remote add origin(remote name) https://github.com/edrez108/Telegram-test.git
# git push -u origin main