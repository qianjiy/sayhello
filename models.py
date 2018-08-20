import time
from orm import (
    Model,
    String, Float, Integer, Boolean
)


class User(Model):
    __table__ = 'users'

    email = String(primary_key=True)
    password = String()
    createTime = Float(default=time.time())


