import uuid
import asyncio
from aiohttp import web
from src.models.llm_tokenizer import LLMTokenizer
from src.config import config
from src.config.types import LLMEventTypes
from cachetools import TTLCache


class AsyncQueueHandler:
    def __init__(self, queue):
        self.queue = queue
        self.loop = asyncio.get_event_loop()

    async def put(self, item):
        return await self.loop.run_in_executor(None, self.queue.put, item)

    async def get(self):
        return await self.loop.run_in_executor(None, self.queue.get)


class ResponseHandler:
    def __init__(self, events_queue, tokenizer):
        self.events_queue = events_queue
        self.tokenizer: LLMTokenizer = tokenizer
        self.execution_queues = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)

    async def listen(self):
        while True:
            queue_event = await self.events_queue.get()  # Get the event from the multiprocessing queue
            if queue_event is None:
                # Send all listeners end event
                for queue in self.execution_queues.values():
                    await queue.put(None)
                break

            execution_id = queue_event["execution_id"]

            if queue_event["events_type"] == LLMEventTypes.INITIALIZED:
                for event in queue_event["events"]:
                    if event:
                        event['text'] = self.tokenizer.decode_output(event['tokens'])

            elif queue_event["events_type"] == LLMEventTypes.PROGRESS:
                for event in queue_event["events"]:
                    if event:
                        event['text'] = self.tokenizer.decode_output(event['token'])

            elif queue_event["events_type"] == LLMEventTypes.COMPLETE:
                for event in queue_event["events"]:
                    if event:
                        event['text'] = self.tokenizer.decode_output(event['tokens'])

            # Route the event to the appropriate execution queue if it exists
            if execution_id in self.execution_queues:
                await self.execution_queues[execution_id].put(queue_event)

    def register_execution(self, execution_id):
        self.execution_queues[execution_id] = asyncio.Queue()
        return self.execution_queues[execution_id]

    def unregister_execution(self, execution_id):
        if execution_id in self.execution_queues:
            del self.execution_queues[execution_id]


class ExecutionHandler:
    def __init__(self, app):
        self.app = app

    async def execute_prompts(self, request_ids, prompts, execution_config, use_stream=True):
        tokenizer: LLMTokenizer = self.app["tokenizer"]
        encoded_dict = tokenizer.tokenize_prompts(prompts)
        listener, execution_id = self.create_listener()

        await self.send_to_execution({
            "execution_id": execution_id,
            "request_ids": request_ids,
            "tokens": encoded_dict["input_ids"],
            "masks": encoded_dict["attention_mask"],
            "config": execution_config,
            "use_stream": use_stream
        })
        return listener, lambda: self.remove_listener(execution_id)

    def create_listener(self):
        response_events: ResponseHandler = self.app["response_events"]
        execution_id = uuid.uuid4()
        return response_events.register_execution(execution_id), execution_id

    def remove_listener(self, execution_id):
        response_events: ResponseHandler = self.app["response_events"]
        response_events.unregister_execution(execution_id)

    async def send_to_execution(self, data):
        await self.app["execution_queue"].put(data)
