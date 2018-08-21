from aiohttp import web
from conf.base import ERROR_CODE
from models import User
from log.log import get_logger
from common.common import http_response
import redis

logger = get_logger('user')
routes = web.RouteTableDef()


@routes.post('/user/signup')
async def signup(request):
    try:
        args = await request.json()
        name = args['name']
        email = args['email']
        password = args['password']
    except :
        logger.info('signup: %s' % ERROR_CODE['1001'])
        return http_response(ERROR_CODE['1001'], 1001)
    # todo check if email is valid
    user = await User.find_first(dict(email=email))
    if user:
        logger.info('signup: %s' % ERROR_CODE['1002'])
        return http_response(ERROR_CODE['1002'], 1002)
    else:
        user = User(name=name, email=email, password=password)
        await user.save()
        logger.info('signup: %s' % ERROR_CODE['0'])
        return http_response(ERROR_CODE['0'], 0)


@routes.post('/user/login')
async def login(request):
    try:
        args = await request.json()
        email = args['email']
        password = args['password']
    except:
        logger.info('login: %s' % ERROR_CODE['1001'])
        return http_response(ERROR_CODE['1001'], 1001)
    redis_pass = await redis.logged(email)
    if redis_pass:
        if redis_pass == password:
            logger.info('login: %s' % ERROR_CODE['1006'])
            return http_response(ERROR_CODE['1006'], 1006)
        else:
            logger.info('login: %s' % ERROR_CODE['1004'])
            return http_response(ERROR_CODE['1004'], 1004)
    user = await User.find_first(dict(email=email))
    if not user:
        logger.info('login: %s' % ERROR_CODE['1003'])
        return http_response(ERROR_CODE['1003'], 1003)
    if user.password != password:
        logger.info('login: %s' % ERROR_CODE['1004'])
        return http_response(ERROR_CODE['1004'], 1004)
    logger.info('login: %s %s ' % (email, ERROR_CODE['0']))
    await redis.login_cache(email, password)
    return http_response(ERROR_CODE['0'], 0)


@routes.post('/user/logout')
async def logout(request):
    try:
        args = await request.json()
        email = args['email']
        password = args['password']
    except :
        logger.info('logout: %s' % ERROR_CODE['1001'])
        return http_response(ERROR_CODE['1001'], 1001)
    logger.info('logout: %s %s ' % (email, ERROR_CODE['0']))
    res = await redis.logout(email, password)
    if not res:
        return http_response(ERROR_CODE['1005'], 1005)
    return http_response(ERROR_CODE['0'], 0)
