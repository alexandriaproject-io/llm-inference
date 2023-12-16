from src.models.llm_model_class import LLMModel, TokenStreamer
import config
import queue
import threading
import enum

llm_model: LLMModel
execution_queue = queue.Queue()
response_queue = queue.Queue()


class LLMEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5


def init_llm_model():
    global llm_model
    llm_model = LLMModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
    llm_model.load_model()
    llm_model.run_model()

    threading.Thread(target=handle_model_generation, daemon=True).start()


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        response_queue.put({
            "type": LLMEventTypes.START,
            "execution_id": request["execution_id"]
        }),

        stream = TokenStreamer(
            lambda values: response_queue.put({
                "execution_id": request["execution_id"],
                "type": LLMEventTypes.INITIALIZED,
                "tokens": values
            }),
            lambda values: response_queue.put({
                "execution_id": request["execution_id"],
                "type": LLMEventTypes.PROGRESS,
                "tokens": values
            })
        )

        sequences, past_key_values = llm_model.generate_cache(
            request["tokens"],
            request["masks"],
            request.get("values", None),
            request["config"],
            stream
        )

        response_queue.put({
            "execution_id": request["execution_id"],
            "type": LLMEventTypes.COMPLETE,
            "sequences": sequences,
            "past_key_values": past_key_values
        }),
