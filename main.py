from torch.multiprocessing import Process, Queue, Event
from src.services.inference_service.inference_service import start_model_generator
from src.services.api_service.api_service import start_server
from src.utils.logger import log
import transformers
transformers.logging.set_verbosity_error()

if __name__ == '__main__':
    try:
        execution_queue = Queue()
        events_queue = Queue()
        startup_queue = Queue()

        print("Lading LLM inference service\n")
        llm_process = Process(
            target=start_model_generator,
            args=(execution_queue, events_queue, startup_queue),
            daemon=True,
        )
        llm_process.start()
        # Set the LLM process to the highest priority (Unix/Linux)
        # psutil.Process(llm_process.pid).nice(psutil.HIGH_PRIORITY_CLASS)  # -20 or psutil.HIGH_PRIORITY_CLASS for Windows
        thread_status = startup_queue.get()
        if not thread_status.get("success", False):
            log.error(thread_status.get("error", "Unknown error"))
            exit(1)

        print("Starting API service")
        api_process = Process(
            target=start_server,
            args=(execution_queue, events_queue),
            daemon=True,
        )
        api_process.start()

        # Set the API process to the lowest priority (Unix/Linux)
        # psutil.Process(api_process.pid).nice(psutil.IDLE_PRIORITY_CLASS)    # 19 or psutil.HIGH_PRIORITY_CLASS for Windows

        api_process.join()
        llm_process.join()
    except KeyboardInterrupt:
        print("Goodbye...")
