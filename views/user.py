from aiohttp import web
from conf.base import ERROR_CODE
from models import User
from log.log import get_logger

logger = get_logger('user')
routes = web.RouteTableDef()


def response(msg, code):
    data = {
        'data': {
            'msg': msg,
            'code': code
        }
    }
    return web.json_response(data)


@routes.post('/user/signup')
async def signup(request):
    try:
        args = await request.json()
        email = args['email']
        password = args['password']
        print(email, password)
        user = await User.find(email)
        if user:
            logger.info('signup: %s' % ERROR_CODE['1002'])
            return response(ERROR_CODE['1002'], 1002)
        else:
            user = User(email=email, password=password)
            await user.save()
    except:
        logger.info('signup: %s' % ERROR_CODE['1001'])
        return response(ERROR_CODE['1001'], 1001)
    logger.info('signup: %s' % ERROR_CODE['0'])
    return response(ERROR_CODE['0'], 0)


@routes.post('/user/login')
async def login(request):
    try:
        args = await request.json()
        email = args['email']
        password = args['password']
        user = await User.find(email)
        if not user:
            logger.info('login: %s' % ERROR_CODE['1003'])
            return response(ERROR_CODE['1003'], 1003)
        if user.password != password:
            logger.info('login: %s' % ERROR_CODE['1004'])
            return response(ERROR_CODE['1004'], 1004)
    except:
        logger.info('login: %s' % ERROR_CODE['1001'])
        return response(ERROR_CODE['1001'], 1001)
    logger.info('login: %s %s ' % (email, ERROR_CODE['0']))
    return response(ERROR_CODE['0'], 0)
