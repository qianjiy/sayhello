from importlib import import_module


def include(module):
    res = import_module(module)
    routes = getattr(res, 'routes')
    return routes


def add_routes(app):
    app.add_routes(include('views.user'))
    app.add_routes(include('views.chat'))
