import re
from aiohttp import web
from conf.base import ERROR_CODE
from models import User
import redis

routes = web.RouteTableDef()
name_format = re.compile(r'^[a-zA-Z_][0-9a-zA-Z_]{3,19}$')


# response format
# {"data":"", "msg":"", "code":""}
def response(msg, code, data=''):
    resp = dict(data=data, msg=msg, code=code)
    return web.json_response(resp)


# sign up post format
# {"name":"", "password":""},both are no longer than 20 and no less than 4
# , and name should only contains letter, figure and underline,
# more importantly no Chinese character
@routes.post('/user/signup')
async def signup(request):
    try:
        args = await request.json()
        name = args['name']
        password = args['password']
    except:
        return response(ERROR_CODE['1001'], 1001)
    if not name_format.match(name):
        return response(ERROR_CODE['1006'], 1006, name)
    if len(password) < 6:
        return response(ERROR_CODE['1007'], 1007)
    user = await User.find_first(dict(name=name))
    if user:
        return response(ERROR_CODE['1002'], 1002, name)
    user = User(name=name, password=password)
    res = await user.save()
    if res:
        return response(ERROR_CODE['0'], 0)
    else:
        return response(ERROR_CODE['1005'], 1005)


# format: the same as sign up
@routes.post('/user/login')
async def login(request):
    try:
        args = await request.json()
        name = args['name']
        password = args['password']
    except:
        return response(ERROR_CODE['1001'], 1001)
    user = await User.find_first(dict(name=name))
    if not user:
        # did not signed up
        return response(ERROR_CODE['1003'], 1003, name)
    if user.password != password:
        return response(ERROR_CODE['1004'], 1004)
    # put into redis cache
    res = await redis.set_user(name, password)
    if not res:
        # unknown error, maybe something wrong with redis
        return response(ERROR_CODE['1005'], 1005)
    return response(ERROR_CODE['0'], 0)


@routes.post('/user/change')
async def change_info(request):
    pass


# add friend
@routes.post('/user/add')
async def add_friend(request):
    pass
