import time
from orm import (
    Model,
    String, Float, Integer, Boolean
)


class User(Model):
    __table__ = 'users'

    name = String()
    email = String(primary_key=True)
    password = String()
    createTime = Float(default=time.time())



class Friend(Model):
    __table__ = 'friends'
    # userA and userB store user's name
    emailA = String(name='userA', primary_key=True)
    emailB = String(name='userB')
    addTime = Float(default=time.time())
