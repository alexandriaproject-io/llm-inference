from src.models.llm_model_class import BaseStreamer
import enum


class LLMInternalEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5
    ERROR = 6


class ResponseQueueStreamer(BaseStreamer):
    def __init__(self, queue, execution_id):
        self.queue = queue
        self.execution_id = execution_id

    def put(self, value):
        self.queue.put({
            "type": LLMInternalEventTypes.INITIALIZED if value.dim() == 2 else LLMInternalEventTypes.PROGRESS,
            "execution_id": self.execution_id,
            "tokens": value,
        })


def check_request_cache(cache, request, device):
    if request["cache_id"] in cache:
        cached_item = cache[request["cache_id"]]
        return (
            cached_item["tokens"],
            cached_item["masks"],
            cached_item["values"],
            request["config"] or cached_item["config"],  # Allow for in between cache config changes
        )
    else:
        return (
            request["tokens"].to(device),
            request["masks"].to(device),
            None,
            request["config"] or None,
        )
