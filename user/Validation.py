from sqlalchemy.orm import Session
from typing import List, Optional
import user.Models as User_Models
import user.Schema as User_Schema
from Authjwt import JWT


async def verify_existing_user(phone_number: str, database: Session) -> User_Schema:
    user = database.query(User_Models.User).filter_by(phone_number=phone_number).first()

    return user if user else None


async def verify_password(plain_pass: str, hashed_pass: str):
    return JWT.hasher.verify(plain_pass, hashed_pass)

