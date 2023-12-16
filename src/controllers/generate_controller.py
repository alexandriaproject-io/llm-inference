from aiohttp import web
from aiohttp_swagger import swagger_path
import json
from src.services.model_service import add_prompts_execution, LLMEventTypes


def is_valid_config(generation_config):
    if generation_config:
        if not isinstance(generation_config, dict):
            return False
        for key, value in generation_config.items():
            if key in ['num_beams', 'max_new_tokens', 'top_k'] and not isinstance(value, int):
                return False
            elif key in ['do_sample', 'stream'] and not isinstance(value, bool):
                return False
            elif key in ['temperature', 'top_p', 'repetition_penalty', 'length_penalty'] \
                    and not (isinstance(value, float) or isinstance(value, int)):
                return False
    return True



@swagger_path('src/controllers/swagger/generate_one.yml')
async def generate_one(request):
    try:
        data = await request.json()
        request_id = data.get('request_id')
        prompt = data.get('prompt')
        generation_config = data.get('generation_config', {})

        # Validate payload
        if ((not request_id or not isinstance(request_id, str))
                or (not prompt or not isinstance(prompt, str))
                or (not is_valid_config(generation_config))):
            return web.Response(text="Invalid request_id", status=400)

        # Process the request
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'text/plain'},
        )
        await response.prepare(request)

        response_queue = add_prompts_execution([request_id],[prompt],generation_config)
        while True:
            event = response_queue.get()
            print(event)
            if event.type == LLMEventTypes.COMPLETE:
                break

        return response
    except json.JSONDecodeError:
        return web.Response(text="Invalid JSON format", status=400)





@swagger_path('src/controllers/swagger/generate_batch.yml')
async def generate_batch(request):
    return web.Response(text="Hello, world2")
