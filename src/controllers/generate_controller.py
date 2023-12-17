from aiohttp import web
from aiohttp_swagger import swagger_path
import json
import time
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
        generation_config = data.get('generation_config', None)
        only_new_tokens = isinstance(data.get("only_new_tokens"), bool) and data["only_new_tokens"]
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

        counter = 0
        start_time = time.perf_counter()
        response_queue = add_prompts_execution([request_id], [prompt], generation_config)
        while True:
            event = response_queue.get()
            if event["type"] == LLMEventTypes.START:
                print(f"Handing request {request_id}")
            elif not only_new_tokens and event["type"] == LLMEventTypes.INITIALIZED:
                await response.write(event["text"].encode('utf-8'))
            elif event["type"] == LLMEventTypes.PROGRESS:
                await response.write(event["text"].encode('utf-8'))
                counter += 1
            elif event["type"] == LLMEventTypes.COMPLETE:
                # if event["is_eos"]:
                #    await response.write("</s>".encode('utf-8'))
                break

        end_time = time.perf_counter()
        diff = end_time - start_time
        print(f"Execution of {counter} tokens was {diff} seconds at {counter / diff} t/s")
        await response.write_eof()
        return response
    except json.JSONDecodeError:
        return web.Response(text="Invalid JSON format", status=400)


@swagger_path('src/controllers/swagger/generate_batch.yml')
async def generate_batch(request):
    return web.Response(text="Hello, world2")
