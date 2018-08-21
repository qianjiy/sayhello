import json
from aiohttp import web
from models import User
from common.common import msg_data, http_response
from conf.base import ERROR_CODE
import redis

routes = web.RouteTableDef()


def chat_init(loop):
    global __loop
    __loop = loop


async def error_deal(ws, msg, code):
    await ws.send_json(msg_data(msg, code))
    await ws.close()
    return ws


# msg format
# {"email":"email", "password":"", "to": "{}", "msg":"{detail}"} from client

# msg_format
# {"who": "{to}", "msg": "{detail}"} from msg queue

@routes.post('/chat/send')
async def send_msg(request):
    try:
        args = await request.json()
        email_from = args['email']
        password = args['password']
        email_to = args['to']
        msg = args['msg']
    except:
        return http_response(ERROR_CODE['1001'], 1001)
    redis_pass = await redis.logged(email_from)
    if not redis_pass:
        return http_response(ERROR_CODE['1007'], 1007)
    if redis_pass != password:
        return http_response(ERROR_CODE['1004'], 1004)
    await redis.send_msg(email_from, email_to, msg)
    return http_response(ERROR_CODE['0'], 0)


@routes.get('/chat')
async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    user_info = json.loads(await ws.receive_json())
    try:
        email = user_info['email']
        password = user_info['password']
        user = await User.find_first(dict(email=email))
    except:
        return await error_deal(ws, ERROR_CODE['1001'], 1001)
    if not user:
        return await error_deal(ws, ERROR_CODE['1003'], 1003)
    if user.password != password:
        return await error_deal(ws, ERROR_CODE['1004'], 1004)
    await ws.send_json(msg_data(ERROR_CODE['0'], 0))
    while not ws.closed:
        receive_msg = await redis.get_msg(email)
        if receive_msg:
            print(receive_msg)
            try:
                await ws.send_json(receive_msg)
            except:
                await redis.get_mag_fail(user.email, receive_msg)
    return ws
