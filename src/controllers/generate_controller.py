from aiohttp import web
from aiohttp_swagger import swagger_path
import json
import time
import asyncio
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


def is_valid_batch_item(batch):
    request_id = batch.get("request_id", '')
    prompt = batch.get("prompt", " ")
    return request_id and isinstance(request_id, str) and isinstance(prompt, str)


@swagger_path('src/controllers/swagger/generate_one.yml')
async def generate_one(request):
    try:
        data = await request.json()
        request_id = data.get('request_id')
        prompt = data.get('prompt', ' ')
        generation_config = data.get('generation_config', {})
        only_new_tokens = isinstance(data.get("only_new_tokens"), bool) and data["only_new_tokens"]
        # Validate payload
        if (
                (not request_id or not isinstance(request_id, str))
                or (not prompt or not isinstance(prompt, str))
                or (not is_valid_config(generation_config))
        ):
            return web.Response(text="Invalid Data Format", status=400)

        # Process the request
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'text/plain', 'Transfer-Encoding': 'chunked'},
        )
        await response.prepare(request)
        is_streaming = generation_config.get("num_beams", 1) == 1

        start_time = time.perf_counter()
        response_queue = add_prompts_execution(
            [request_id],
            [prompt],
            generation_config,
            is_streaming
        )

        initialization = ''
        while True:
            await asyncio.sleep(0)  # Streaming work-around - aiohttp needs time to actually send the data
            events = response_queue.get()

            # Stream error as the last chunk before killing the request
            if events["events_type"] == LLMEventTypes.ERROR:
                error_message = str(events.get("error", "Unknown error occurred"))
                print(f"Request {request_id} error: {error_message}")
                await response.write(error_message.encode('utf-8'))
                await asyncio.sleep(0)
                raise Exception(f"Error processing request {request_id}: {error_message}")

            event = events["events"][0]
            if event:
                if event["type"] == LLMEventTypes.START:
                    print(f"Handing request {request_id}")
                elif event["type"] == LLMEventTypes.INITIALIZED:
                    initialization = event["text"]
                    if is_streaming and not only_new_tokens:
                        await response.write(event["text"].encode('utf-8'))
                elif event["type"] == LLMEventTypes.PROGRESS:
                    await response.write(event["text"].encode('utf-8'))
                elif event["type"] == LLMEventTypes.COMPLETE:
                    counter = event['new_tokens_count']
                    if not is_streaming:
                        if not only_new_tokens:
                            await response.write(event["text"].encode('utf-8'))
                        else:
                            await response.write(event["text"].replace(initialization, '').encode('utf-8'))
                    break

        diff = time.perf_counter() - start_time
        print(f"Generation of {counter} tokens was {diff} seconds at {counter / diff} t/s")
        await response.write_eof()
        return response
    except json.JSONDecodeError:
        return web.Response(text="Invalid JSON format", status=400)


@swagger_path('src/controllers/swagger/generate_batch.yml')
async def generate_batch(request):
    try:
        data = await request.json()
        prompts = data.get('prompts', [])
        generation_config = data.get('generation_config', None)
        only_new_tokens = isinstance(data.get("only_new_tokens"), bool) and data["only_new_tokens"]
        # Validate payload
        if (
                (not len(prompts))
                or (not all(is_valid_batch_item(prompt) for prompt in prompts))
                or (not is_valid_config(generation_config))
        ):
            return web.Response(text="Invalid Data Format", status=400)

        request_ids = [item['request_id'] for item in prompts]
        request_prompts = [item['prompt'] for item in prompts]

        if len(request_ids) != len(set(request_ids)):
            return web.Response(text="Duplicate request_ids", status=400)

        start_time = time.perf_counter()
        response_queue = add_prompts_execution(request_ids, request_prompts, generation_config, False)
        initializations = []
        while True:
            events = response_queue.get()
            if events["events_type"] == LLMEventTypes.ERROR:
                error_message = str(events.get("error", "Unknown error occurred"))
                print(f"Requests {', '.join(request_ids)} error: {error_message}")
                await asyncio.sleep(0)
                raise Exception(f"Error processing requests {', '.join(request_ids)}: {error_message}")

            if (events["events_type"]) == LLMEventTypes.INITIALIZED:
                initializations = events["events"]
            elif (events["events_type"]) == LLMEventTypes.COMPLETE:
                results = events["events"]
                counter = events["new_tokens_count"]
                is_complete = events["is_eos_all"]
                break

        diff = time.perf_counter() - start_time
        print(f"Execution of {counter} tokens was {diff} seconds at {counter / diff} t/s")

        remapped_results = []
        for result, initialization in zip(results, initializations):
            remapped_result = {"request_id": result["request_id"]}
            if not only_new_tokens:
                remapped_result["prompt"] = initialization["text"]
            remapped_result["response"] = result["text"].replace(initialization["text"], '')
            remapped_results.append(remapped_result)

        return web.Response(
            text=json.dumps(remapped_results),
            content_type='application/json',
            status=200 if is_complete else 206
        )
    except json.JSONDecodeError:
        return web.Response(text="Invalid JSON format", status=400)
