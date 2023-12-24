import enum
from logger import log
from src.models.llm_model_class import BaseStreamer

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


def check_request_cache(cache, cache_id, request, device):
    if cache_id in cache:
        cached_item = cache[cache_id]
        log.info("Using cached values")
        return (
            cached_item["tokens"],
            cached_item["masks"],
            cached_item["values"],
            request["config"] or cached_item["config"] or {},  # Allow for in between cache config changes
        )
    else:
        log.info("No cached values found")
        return (
            request["tokens"].to(device),
            request["masks"].to(device),
            None,
            request["config"] or {},
        )
