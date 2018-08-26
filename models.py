import time
from orm import (
    Model,
    String, Float, Integer, Boolean
)


class User(Model):
    __table__ = 'users'

    name = String(primary_key=True, length=20)
    password = String(length=20)


class Friend(Model):
    __table__ = 'friends'
    # userA and userB store user's name
    userA = String(length=20, primary_key=True)
    userB = String(length=20)
