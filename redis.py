import aioredis

from conf.base import redis_conf

conf = {
    'msg_que': 'msg_que_%s',
    'msg_format': '{"who": "%s", "msg": %s"}',
    'cache_': 'cache_%s'
}


async def init_redis(loop):
    await create_pool(loop)


async def create_pool(loop):
    global pool
    pool = await aioredis.create_pool(loop=loop, **redis_conf)


async def login_cache(email, password):
    await pool.execute('set', conf['cache_'] % email, password)
    return await pool.execute('expire', conf['cache_'] % email, 86400)  # disappear after 24h


# return logged password
async def logged(email):
    return await pool.execute('get', conf['cache_'] % email)


async def logout(email, password):
    res = await pool.execute('get', conf['cache_'] % email)
    if res and res == password:
        return await pool.execute('del', conf['cache_'] % email)
    return False


async def send_msg(from_user, to_user, msg):
    return await pool.execute('rpush', conf['msg_que'] % to_user, conf['msg_format'] % (from_user, msg))


async def get_msg(user):
    return await pool.execute('lpop', conf['msg_que'] % user)


async def get_mag_fail(user, msg):
    return await pool.execute('lpush', conf['msg_que'] % user, msg)
