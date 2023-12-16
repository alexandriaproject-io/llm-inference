from aiohttp import web

async def generate_one(request):
    return web.Response(text="Hello, world1")




async def generate_batch(request):
    return web.Response(text="Hello, world2")