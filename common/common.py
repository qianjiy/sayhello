from aiohttp import web


def http_response(msg, code):
    return web.json_response(msg_data(msg, code))


def msg_data(msg, code):
    data = {
        'data': {
            'msg': msg,
            'code': code
        }
    }
    return data
