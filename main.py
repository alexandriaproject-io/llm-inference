from torch.multiprocessing import Process, Queue, Event
from src.services.inference_service.inference_service import start_model_generator
from src.services.api_service.api_service import start_server

if __name__ == '__main__':
    execution_queue = Queue()
    events_queue = Queue()
    print("Lading LLM inference service")
    inference_ready_event = Event()
    Process(
        target=start_model_generator,
        args=(execution_queue, events_queue, inference_ready_event)
    ).start()
    inference_ready_event.wait()
    print("Starting API service")
    api_process = Process(
        target=start_server,
        args=(execution_queue, events_queue)
    )
    api_process.start()
    api_process.join()
    print("Done")


