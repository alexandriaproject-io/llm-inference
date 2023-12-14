# Large Language Model Inference Service

This documentation provides an overview of the Large Language Model (LLM) Inference Service, designed to handle asynchronous processing of inference tasks through WebSocket communication. The service architecture is depicted in the UML chart below, illustrating the flow of events and the interaction between the WebSocket client and the LLM Inference Service.

![LLM Inference Service UML Diagram](diagrams/llm-inference-websocket.svg)

## Overview

The service leverages WebSocket for a full-duplex communication channel over a single TCP connection. This allows the client to receive real-time progress updates and results from the LLM.

## Event Types

The communication protocol is event-driven, with three main types of events:

1. `START` Event:
   - Indicates the initiation of a request.
   - Contains a unique `id` for the session.

2. `PROGRESS` Event:
   - Sent for each incremental update during the processing of the request.
   - The `id` matches the `START` event, and `data` contains the incremental output.

3. `COMPLETE` Event:
   - Signifies the completion of the inference process.
   - The `id` corresponds with the initiating `START` event, and `data` holds the final output.
   - An `isEos` boolean flag indicates if the end of the stream has been reached.

## Communication Flow

1. The WebSocket client establishes a connection with the LLM Inference Service.
2. The client sends a `START` event with the initial prompt.
3. The service responds with a series of `PROGRESS` events, each carrying a piece of the generated content.
4. Once the inference is complete, a `COMPLETE` event is sent, marking the end of the session.

Responses from the service are structured as arrays of events, with each event capturing a state change or an update in the processing of the inference task.

## Example

Here is an example of a WebSocket client receiving events from the service:

```json
// Start Event
[
  {
    "type": "START",
    "id": "123",
    "data": "Write a ..."
  }
]

// Progress Events
[{ "type": "PROGRESS", "id": "123", "data": "In" }]
  
[{ "type": "PROGRESS", "id": "123", "data": "the" }]

// Additional progress events...


// Complete Event
[
  {
    "type": "COMPLETE",
    "id": "123",
    "data": "In the realm of",
    "isEos": false
  }
]