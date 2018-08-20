from aiohttp import web
from importlib import import_module
from orm import create_pool


def include(module):
    res = import_module(module)
    routes = getattr(res, 'routes')
    return routes


async def make_app():
    app = web.Application()
    await create_pool(app.loop)
    app.add_routes(include('views.user'))
    return app
