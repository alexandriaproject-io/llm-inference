namespace java com.inference.websocket

include "com.inference.common.thrift" // Include your common definitions here

struct WsInferenceRequest {
  1: list<com.inference.common.SinglePrompt> prompts;
  2: optional bool stream_response; // Stream generated tokens one by one
  3: optional bool only_new_tokens; // Only return generated tokens or return prompt + generated tokens
  4: optional com.inference.common.GenerationConfig generation_config;
}

struct WsInferenceAcceptedEvent {
  1: string request_id; // Id to identify the request
}

struct WsInferenceStartedEvent {
  1: string request_id; // Id to identify the request
}

struct WsInferenceInitializedEvent {
  1: string request_id; // Id to identify the request
  3: string text; // Initial prompt if only_new_tokens is false else ''
}

struct WsInferenceProgressEvent {
  1: string request_id; // Id to identify the request
  3: string text; // Generated token text
}

struct WsInferenceCompletionEvent {
  1: string request_id; // Id to identify the request
  3: string text; // Generated response text
  4: bool is_eos; // Is End of Sentence - did the model finish execution or not
  5: i32 new_tokens_count; // Count of newly generated tokens
  6: double execution_time; // Time it took the model to generate the response
}

struct WsInferenceErrorEvent {
  1: string request_id; // Id to identify the request
  3: string error; // Error description
}

struct WsErrorEvent {
  3: string error; // Error description
}

union WsInferenceEvent {
  1: WsInferenceAcceptedEvent acceptedEvent;
  2: WsInferenceStartedEvent startedEvent;
  3: WsInferenceInitializedEvent initializedEvent;
  4: WsInferenceProgressEvent progressEvent;
  5: WsInferenceCompletionEvent completionEvent;
  6: WsInferenceErrorEvent errorEvent;
  7: WsInferenceErrorEvent wsErrorEvent;
}

struct WsInferenceResponse {
  1: list<WsInferenceEvent> events;
}
