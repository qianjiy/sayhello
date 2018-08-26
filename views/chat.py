from aiohttp import web, WSMsgType
from conf.base import ERROR_CODE
import redis

routes = web.RouteTableDef()


# response format
# {"data":"", "msg":"", "code":""}
async def error(ws, msg, code, data=''):
    resp = dict(data=data, msg=msg, code=code)
    await ws.send_json(resp)
    await ws.close()
    return ws


# msg format
# {"to":"", "msg":""}
# {"from":"", "msg":""}
@routes.get('/chat')
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    try:
        user_info = await ws.receive_json()
        name = user_info['name']
        password = user_info['password']
    except:
        return await error(ws, ERROR_CODE['1001'], 1001)
    cache_pass = await redis.get_user_password(name)
    if cache_pass != password:
        return await error(ws, ERROR_CODE['1004'], 1004)
    request.app['websockets'][name] = ws
    # get cache message
    cache_msg = await redis.get_msg(name)
    print(cache_msg)
    for m in cache_msg:
        try:
            await ws.send_str(m)
        except:
            await redis.get_error(name, m)
    async for msg in ws:
        if msg.type == WSMsgType.text:
            try:
                m = msg.json()
                to_user = m['to']
                content = m['msg']
            except:
                return await error(ws, ERROR_CODE['1001'], 1001)
            # todo check relation ship
            if to_user in request.app['websockets'].keys() and not request.app['websockets'][to_user].closed:
                try:
                    print(name + 'online to' + to_user, request.app['websockets'][to_user].closed)
                    await request.app['websockets'][to_user].send_json({"from": name, "msg": content})
                except:
                    print(name + 'error to' + to_user)
                    await redis.set_msg(name, to_user, content)
            else:
                print('off to' + to_user)
                await redis.set_msg(name, to_user, content)
        else:
            print('error with' + name)
            break
    del request.app['websockets'][name]
    print('close' + name)
    return ws
