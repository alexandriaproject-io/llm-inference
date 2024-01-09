from aiohttp import web
import asyncio
import json
from logger import log
from src.config.types import LLMEventTypes
from src.controllers.controller_utils import is_valid_batch, is_valid_config

async def handle_message(ws, data, executions, use_thrift):
    prompts = data.get('prompts', [])
    generation_config = data.get('generation_config', None)
    only_new_tokens = data.get("only_new_tokens", True) if isinstance(data.get("only_new_tokens"), bool) else True
    stream_response = data.get("stream_response", True) if isinstance(data.get("stream_response"), bool) else True

    if not is_valid_batch(prompts) or not is_valid_config(generation_config):
        await ws.send_str('{"error": "Invalid prompts or generation_config"}')
        return

    request_ids = [item['request_id'] for item in prompts]
    request_prompts = [item['prompt'] for item in prompts]
    await ws.send_str(json.dumps([{"request_id": request_id, "type": 'ACCEPTED'} for request_id in request_ids]))

    response_queue, remove_queue = await executions.execute_prompts(
        request_ids,
        request_prompts,
        generation_config,
        stream_response
    )
    initializations = []

    while True:
        events = await response_queue.get()
        if ws.closed:
            break

        if events is None:
            await ws.send_str('{"error": "Server is shutting down."}')
            await ws.close()
            break

        if events["events_type"] == LLMEventTypes.ERROR:
            error_message = str(events.get("error", "Unknown error occurred"))
            log.error(f"Requests {', '.join(request_ids)} error: {error_message}")
            error_events = [{
                "request_id": event["request_id"],
                "type": "ERROR",
                "error": str(event["error"])
            } for event in events["events"] if event is not None]
            await ws.send_json(error_events)
            break

        elif events["events_type"] == LLMEventTypes.START:
            log.info(f"Handing requests {', '.join(request_ids)}")
            start_events = [{
                "request_id": event["request_id"],
                "type": "STARTED"
            } for event in events["events"] if event is not None]
            await ws.send_json(start_events)

        elif (events["events_type"]) == LLMEventTypes.INITIALIZED:
            initializations = events["events"]
            if stream_response:
                initialized_events = [{
                    "request_id": event["request_id"],
                    "text": event["text"] if not only_new_tokens else '',
                    "type": "INITIALIZED"
                } for event in events["events"] if event is not None]
                await ws.send_json(initialized_events)

        elif (events["events_type"]) == LLMEventTypes.PROGRESS:
            if stream_response:
                progress_events = [{
                    "request_id": event["request_id"],
                    "text": event["text"],
                    "type": "PROGRESS"
                } for event in events["events"] if event is not None]
                await ws.send_json(progress_events)

        elif (events["events_type"]) == LLMEventTypes.COMPLETE:
            complete_events = [{
                "request_id": event["request_id"],
                "text": event["text"].replace(initialization["text"], '') if only_new_tokens else event["text"],
                "is_eos": event["is_eos"],
                "new_tokens_count": event["new_tokens"],
                "execution_time": event["execution_time"],
                "type": "COMPLETE"
            } for event, initialization in zip(events["events"], initializations) if event is not None]
            await ws.send_json(complete_events)
            total_count = sum(result['new_tokens'] for result in events["events"])
            log.info(
                f"Execution took of {total_count} tokens was {events['execution_time']} sec at {total_count / events['execution_time']} t/s")
            break
    remove_queue()


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    executions = request.executions
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                asyncio.create_task(handle_message(ws, data, executions, False))
            except json.JSONDecodeError:
                await ws.send_str('{"error": "Invalid JSON received"}')
        elif msg.type == web.WSMsgType.ERROR:
            print('WebSocket connection closed with exception %s' % ws.exception())

    print('WebSocket connection closed')
    return ws
