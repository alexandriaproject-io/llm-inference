from aiohttp import web
import asyncio
import json
from src.utils.logger import log
from src.config.types import LLMEventTypes
from src.controllers.controller_utils import is_valid_batch, is_valid_config
from thrift.Thrift import TException
from src.utils.thrift_dict import thrift_to_dict, thrift_read, thrift_to_binary
from com.inference.ws.ttypes import (
    WsInferenceRequest,
    WsInferenceResponse,
    WsErrorEvent,
    WsInferenceAcceptedEvent,
    WsInferenceStartedEvent,
    WsInferenceInitializedEvent,
    WsInferenceProgressEvent,
    WsInferenceCompletionEvent,
    WsInferenceErrorEvent,
)


def list_to_thrift_ws_response(event_dicts, thrift_event_class):
    response = WsInferenceResponse()
    response.events = []

    for event_dict in event_dicts:
        event_record = thrift_event_class()
        for key, value in event_dict.items():
            if hasattr(event_record, key):
                setattr(event_record, key, value)
        response.events.append(event_record)

    return response


async def ws_send_response(ws, data_json, thrift_class=None, send_binary=False):
    if send_binary and thrift_class is not None:
        ws_response = list_to_thrift_ws_response(data_json, thrift_class)
        await ws.send_bytes(thrift_to_binary(ws_response))
    else:
        await ws.send_json(data_json)


async def handle_message(ws, data, executions, use_thrift):
    prompts = data.get('prompts', [])
    generation_config = data.get('generation_config', None)
    only_new_tokens = data.get("only_new_tokens", True) if isinstance(data.get("only_new_tokens"), bool) else True
    stream_response = data.get("stream_response", True) if isinstance(data.get("stream_response"), bool) else True

    if not is_valid_batch(prompts) or not is_valid_config(generation_config):
        error_json = [{"error": "Invalid prompts or generation_config"}]
        await ws_send_response(ws, error_json, WsErrorEvent, use_thrift)
        return

    request_ids = [item['request_id'] for item in prompts]
    request_prompts = [item['prompt'] for item in prompts]
    response_queue, remove_queue = await executions.execute_prompts(
        request_ids,
        request_prompts,
        generation_config,
        stream_response
    )

    accepted_json = [{"request_id": request_id, "type": 'ACCEPTED'} for request_id in request_ids]
    await ws_send_response(ws, accepted_json, WsInferenceAcceptedEvent, use_thrift)

    initializations = []

    while True:
        events = await response_queue.get()
        if ws.closed:
            break

        if events is None:
            error_json = [{"error": "Server is shutting down."}]
            await ws_send_response(ws, error_json, WsErrorEvent, use_thrift)
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
            await ws_send_response(ws, error_events, WsInferenceErrorEvent, use_thrift)
            break

        elif events["events_type"] == LLMEventTypes.START:
            log.info(f"Handing requests {', '.join(request_ids)}")
            start_events = [{
                "request_id": event["request_id"],
                "type": "STARTED"
            } for event in events["events"] if event is not None]
            await ws_send_response(ws, start_events, WsInferenceStartedEvent, use_thrift)

        elif (events["events_type"]) == LLMEventTypes.INITIALIZED:
            initializations = events["events"]
            if stream_response:
                initialized_events = [{
                    "request_id": event["request_id"],
                    "text": event["text"] if not only_new_tokens else '',
                    "type": "INITIALIZED"
                } for event in events["events"] if event is not None]
                await ws_send_response(ws, initialized_events, WsInferenceInitializedEvent, use_thrift)

        elif (events["events_type"]) == LLMEventTypes.PROGRESS:
            if stream_response:
                progress_events = [{
                    "request_id": event["request_id"],
                    "text": event["text"],
                    "type": "PROGRESS"
                } for event in events["events"] if event is not None]
                await ws_send_response(ws, progress_events, WsInferenceProgressEvent, use_thrift)

        elif (events["events_type"]) == LLMEventTypes.COMPLETE:
            complete_events = [{
                "request_id": event["request_id"],
                "text": event["text"].replace(initialization["text"], '') if only_new_tokens else event["text"],
                "is_eos": event["is_eos"],
                "new_tokens_count": event["new_tokens"],
                "execution_time": event["execution_time"],
                "type": "COMPLETE"
            } for event, initialization in zip(events["events"], initializations) if event is not None]
            await ws_send_response(ws, complete_events, WsInferenceCompletionEvent, use_thrift)
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
                error_json = [{"error": "Invalid JSON received"}]
                await ws_send_response(ws, error_json)
            except Exception as e:
                error_json = [{"error": "Something broke"}]
                await ws_send_response(ws, error_json)
        elif msg.type == web.WSMsgType.BINARY:
            try:
                record = thrift_read(msg.data, WsInferenceRequest)
                asyncio.create_task(handle_message(ws, thrift_to_dict(record), executions, True))
            except TException:
                error_json = [{"error": "Invalid Thrift message received"}]
                await ws_send_response(ws, error_json, WsErrorEvent, True)
            except Exception as e:
                error_json = [{"error": "Something broke"}]
                await ws_send_response(ws, error_json, WsErrorEvent, True)
        elif msg.type == web.WSMsgType.ERROR:
            print('WebSocket connection closed with exception %s' % ws.exception())

    print('WebSocket connection closed')
    return ws
