namespace java com.inference.rest

include "com.inference.common.thrift"

struct ApiSinglePromptRequest {
  1: required string request_id; // Id to identify the request
  2: optional string prompt;     // Request prompt
  3: optional bool stream_response; // Stream generated tokens one by one
  4: optional bool only_new_tokens; // Only return generated tokens or return prompt + generated tokens
  5: optional com.inference.common.GenerationConfig generation_config;
}

struct ApiSinglePromptStream {
   1: string text;  // Generated token text
}

struct ApiBatchPromptRequest {
  1: list<com.inference.common.SinglePrompt> prompts; // Array of SinglePrompt
  2: optional bool only_new_tokens; // Only return generated tokens or return prompt + generated tokens
  3: optional com.inference.common.GenerationConfig generation_config;
}

struct ApiBatchPrompt {
  1: string request_id,         // Id to identify the request
  2: optional string prompt,    // Request prompt if only_new_tokens is set to false
  3: string response            // Generated response text
}

struct ApiBatchPromptResponse {
  1: list<ApiBatchPrompt> responses; // List of responses
}
