# Large Language Model ( LLM ) Inference Architecture

This architecture is specifically designed to maximize the efficiency and throughput of our Large Language Model inference system, ensuring optimal performance and resource utilization even under the constraints of parallel prompt processing.

## LLM Inference Architecture diagram

![Alt text](diagrams/llm-inference-diagram-light.svg)

## Overview
The architecture of our service is designed to support both REST API and WebSocket interfaces for efficient external communication and control. Despite the apparent complexity, this structure stems from the intrinsic functioning of AI inference, particularly in handling parallel prompts.


## Prompt Processing and Execution Workflow
Upon receiving a prompt, each identified by a unique ID, the service initiates a caching check. This process involves comparing the received prompt ID against the existing cache to determine if new tensor generation is needed or if cached data can be utilized. Post this validation, the tensor token values, along with the prompt ID, are queued for execution.

The service is designed to continuously accept and process incoming requests, even when the main thread is engaged. The execution model, operating on a separate thread, monitors the execution queue. If the queue is not empty, or if the model is actively processing a task, it sequentially retrieves and processes each queued item.

During execution, the model emits generated tokens progressively throughout the generation phase. Upon completion, the prompt ID and its corresponding new prompt values are stored in the cache. The final data is then relayed back to the client.

## Challenge of Parallel Prompt Processing
One of the primary challenges in our system is the inefficiency in processing parallel prompts. Typically, when the system handles a single request at a time, there is a significant amount of idle time primarily due to communication overheads. For instance, if token generation requires 20 seconds and request/reply handling adds an extra 10 milliseconds, the model experiences a 33% idle time.

## Optimization through Threading and Execution Queue
To mitigate this issue and optimize model utilization, our system employs a threading mechanism coupled with an internal execution queue. This setup allows the system to process multiple requests simultaneously. While the model is busy executing the first request, the system can prepare the second request in a separate thread. As soon as the first request is completed and sent out, the model can immediately switch to the next request in the queue. This approach ensures minimal idle time for the model, particularly when handling two or more active requests, thereby enhancing token generation efficiency.

## Tensor Values Caching
Our system leverages model caching capabilities to enhance generation speed and memory efficiency. The impact of caching varies based on the max_token size and execution parameters. For example:

Processing 1 token at a time for a total of 731 tokens showed a notable performance improvement with caching: 16.2 seconds with cache versus 33.65 seconds without cache. Additionally, memory usage was lower with caching (not exceeding 14.2GB) compared to non-cached execution (above 16GB).
In contrast, processing 731 tokens in a single iteration displayed no significant difference between cached and non-cached executions, indicating that caching does not impose a considerable performance penalty in such scenarios.


