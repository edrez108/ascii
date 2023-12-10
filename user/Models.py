from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Database import Base
from typing import Optional


class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, default="Unknown")
    phone_number = Column(String, unique=True)
    password = Column(String)

    def __init__(self, phone_number, password):
        self.phone_number = phone_number
        self.password = password

    def __repr__(self):
        print(f"user with phone {self.phone_number} and password{self.password}")
