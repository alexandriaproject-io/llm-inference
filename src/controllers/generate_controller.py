from aiohttp import web
from aiohttp_swagger import swagger_path
import json

@swagger_path('src/controllers/swagger/generate_one.yml')
async def generate_one(request):
    try:
        data = await request.json()
        request_id = data.get('request_id')
        prompt = data.get('prompt')

        # Validate payload
        if not request_id or not isinstance(request_id, str):
            return web.Response(text="Invalid request_id", status=400)
        if not prompt or not isinstance(prompt, str):
            return web.Response(text="Invalid prompt", status=400)

        # Process the request (your logic here)
        return web.Response(text="Hello, world1")
    except json.JSONDecodeError:
        return web.Response(text="Invalid JSON format", status=400)

    return web.Response(text="Hello, world1")



@swagger_path('src/controllers/swagger/generate_batch.yml')
async def generate_batch(request):
    return web.Response(text="Hello, world2")