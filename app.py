from aiohttp import web
from importlib import import_module


def include(module):
    res = import_module(module)
    routes = getattr(res, 'routes')
    return routes


def make_app():
    app = web.Application()
    app.add_routes(include('view.user'))
    return app
