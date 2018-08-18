from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/signup')
async def signup(request):
    return web.Response(text='hello')
