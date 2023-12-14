# Large Language Model Inference Service Documentation

The LLM Inference Service provides two primary endpoints for generating text: a single prompt endpoint and a batch prompt endpoint. The service architecture is designed to handle requests efficiently and return generated text through HTTP streaming or in a full response.
 
## Endpoints
- `POST /api/generate-one`: For generating text from a single prompt.
- `POST /api/generate-batch`: For generating text from multiple prompts in a batch.

## Response Codes
Both endpoints use standard HTTP response codes to indicate the status of a request:

- `200 OK`: The request has been successfully processed, and the response body contains the generated text, which was concluded because the end of the sequence (`eos`) was reached.
- `206 Partial Content`: This status code is returned when a response is streamed back in chunks or if the request has been partially fulfilled due to reaching the maxLength limit specified in the request.
![Single Inference UML Diagram](path-to-single-inference-image)
  
## HTTP Streaming
The single endpoint (`POST /api/generate-one`) supports HTTP streaming, allowing clients to receive the response in a streamed fashion as the text is being generated. This method is especially useful when dealing with large texts or when real-time processing is desired.

## Batch Processing
The batch endpoint (`POST /api/generate-batch`) does not support HTTP streaming. When using this endpoint, the entire response, which includes generated text for all prompts in the batch, is returned once processing is complete.

## Notes on Service Behavior
- The service returns text directly in the response body, not wrapped in JSON.
- HTTP streaming, as depicted in the UML sequence diagrams, represents the service sending data in chunks, not the `206 Partial Content` responses.

## UML Diagrams

### Single Prompt Generation Flow

![LLM Inference Service Workflow](diagrams/rest-api-single-prompt.svg)

### Workflow Description

- **HTTP Request (POST /api/generate-one)**: The client initiates the workflow by sending a POST request to
  the `/api/generate-one` endpoint. The request payload must include a unique `id` for the session, the `prompt` for the
  LLM to process, and a `maxLength` parameter that defines the limit of the generated content's length.

- **LLM Inference Service**: Upon receiving the POST request, our inference service begins the process of generating a
  response. It analyzes the provided prompt and composes a response in real-time.

- **Response Stream**: For single-prompt inferences, the response is streamed back to the client as it's being
  generated. This allows the client to receive immediate feedback and ensures a responsive user experience.

- **Return Status**: Once the full response is composed, the service sends a return status code. A `200` status code
  indicates a successful operation, whereas a `206` status indicates a partial content response, which may occur if the
  response is truncated due to the `maxLength` restriction.

- **End of Request**: The transaction concludes when the full response has been delivered to the client, marked by the
  end of the request.

### API Response Examples

The API responds with text based on the given prompt. Below are two examples:

- For a prompt with `id: 123`, requesting a maximum length of 10, the service might
  return: `Response: "In the realm of code and byte,"`

- For a prompt with `id: 456`, with a `maxLength` of 4, the service might return: `Response: "In the garden where"`

### Implementation Notes

- Responses are dependent on the `prompt` and `maxLength` parameters.
- The service supports single prompt inference; streaming is not available for multiple prompts.
- Ensure your API calls handle both full responses and partial content scenarios gracefully.

## Batch Prompt Generation Flow
![LLM Batch Inference Service Workflow](diagrams/rest-api-batch-prompt.svg)

### Batch Workflow Description

- **HTTP Request (POST /api/generate-batch)**: Clients can send a batch of prompts in a single POST request to the `/api/generate-batch` endpoint. The request payload includes an array of `prompts`, each with a unique `id` and `prompt` text, along with a shared `maxLength` parameter for the batch.

- **LLM Inference Service**: The inference service receives the batch request and processes each prompt concurrently, optimizing for time efficiency.

- **Response**: Unlike the single prompt workflow, batch processing does not support HTTP streaming. The responses for all prompts are compiled into a single response payload and sent back to the client once all prompts have been processed.

- **Return Status**: The service returns a `200` status code for a successful operation or `206` if some responses exceed the `maxLength` and are truncated.

- **Full Response**: The complete batch response is delivered to the client as an array of objects, each containing the `id` of the prompt and the generated `data`.

### API Response Examples for Batch Processing

Here is an example of a batch request and its corresponding response:

#### Batch Request Payload

```json
{
  "prompts": [
    {"id": "123", "prompt": "Write a ...", "maxLength": 10},
    {"id": "456", "prompt": "Write a ...", "maxLength": 10},
    {"id": "789", "prompt": "What is ...", "maxLength": 3}
  ]
}
```

Batch Response:
```json
[
  {"id": "123", "data": "In the realm of code and byte,"},
  {"id": "456", "data": "In the garden"},
  {"id": "789", "data": "Sure! here"}
]
```

### Implementation Notes for Batch Processing
- The batch endpoint is best used for applications requiring the processing of multiple prompts where immediate response for each is not critical.
- Streaming of responses is not supported in batch mode; the entire response set is delivered at once.
- Ensure that your implementation can parse and handle an array of responses, associating each response with its corresponding prompt.
