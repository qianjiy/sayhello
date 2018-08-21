#!/usr/bin/env python3
import asyncio
from aiohttp import web

from orm import init_db
from redis import init_redis
from route import add_routes
from log.log import get_logger
from views.chat import chat_init

logger = get_logger()


async def init(loop):
    app = web.Application(loop=loop)
    add_routes(app)
    chat_init(loop)
    await init_db(loop)
    await init_redis(loop)
    logger.info("sayhello started")
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    web.run_app(app=init(loop), port=80)
