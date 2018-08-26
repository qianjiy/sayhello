#!/usr/bin/env python3
import asyncio
from aiohttp import web

from orm import init_db
from redis import init_redis
from route import add_routes


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


async def init():
    app = web.Application()
    add_routes(app)
    app['websockets'] = {}
    app.on_shutdown.append(shutdown(app))
    await init_db(app.loop)
    await init_redis(app.loop)
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    web.run_app(app=init(), port=80)
