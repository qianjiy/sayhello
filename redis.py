import aioredis
from conf.base import redis_conf


async def init_redis(loop):
    await create_pool(loop)


async def create_pool(loop):
    global pool
    pool = await aioredis.create_pool(loop=loop, **redis_conf)


# user cache format
# user_name password
async def set_user(name, password):
    await pool.execute('set', 'user_{}'.format(name), password)
    # cache will disappear in 24 hours
    return await pool.execute('expire', 'user_{}'.format(name), 86400)


# get the password of the user, if it is in cache, otherwise return None
async def get_user_password(name):
    return await pool.execute('get', 'user_{}'.format(name))


# msg format:
# msg queue : user_msg_name
# {"from":"", "msg":""}
async def set_msg(from_user, to_user, msg):
    return await pool.execute('rpush', 'user_msg_{}'.format(to_user),
                              '{"from": "%s", "msg": "%s"}' % (from_user, msg))


async def get_msg(user):
    print('user_msg_{}'.format(user))
    res = await pool.execute('lrange', 'user_msg_{}'.format(user), 0, -1)
    await pool.execute('del', 'user_msg_{}'.format(user))
    return res


async def get_error(user, msg):
    return await pool.execute('rpush', 'user_msg_{}'.format(user), msg)
