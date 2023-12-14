# Service API Inference Workflow

## Overview

The following UML sequence diagram illustrates the interaction flow between the client and our Language Learning Model (
LLM) Inference Service when generating responses via our API.

![LLM Inference Service Workflow](diagrams/rest-api-single-prompt-dark.svg)

## Workflow Description

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

## API Response Examples

The API responds with text based on the given prompt. Below are two examples:

- For a prompt with `id: 123`, requesting a maximum length of 10, the service might
  return: `Response: "In the realm of code and byte,"`

- For a prompt with `id: 456`, with a `maxLength` of 4, the service might return: `Response: "In the garden where"`

## Implementation Notes

- Responses are dependent on the `prompt` and `maxLength` parameters.
- The service supports single prompt inference; streaming is not available for multiple prompts.
- Ensure your API calls handle both full responses and partial content scenarios gracefully.

## Batch Processing API Inference Workflow

### Overview

In addition to single prompt processing, our service also supports batch processing, allowing multiple prompts to be processed in a single API call. The UML diagram below depicts the batch processing workflow.

![LLM Batch Inference Service Workflow](diagrams/rest-api-batch-prompt-dark.svg)

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

## Implementation Notes for Batch Processing
- The batch endpoint is best used for applications requiring the processing of multiple prompts where immediate response for each is not critical.
- Streaming of responses is not supported in batch mode; the entire response set is delivered at once.
- Ensure that your implementation can parse and handle an array of responses, associating each response with its corresponding prompt.