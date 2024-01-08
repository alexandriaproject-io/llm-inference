namespace java com.inference.common

struct SinglePrompt {
  1: required string request_id; // Id to identify the request
  2: optional string prompt;     // Request prompt text
}

struct GenerationConfig {
  1: optional i32 num_beams;  // Number of beams for beam search. More beams increase diversity of results, but slower generation.
  2: optional bool do_sample; // Whether to use sampling; set to true to have more diverse results, false for deterministic output.
  3: optional double temperature; // Controls randomness: Lower closer to 0 means less random, higher means more random. Requires do_sample:true
  4: optional double top_p; // Nucleus sampling: higher means more diversity, lower means closer to greedy decoding.
  5: optional i32 top_k; // Top-k sampling: the number of highest probability vocabulary tokens to keep for top-k-filtering.
  6: optional i32 max_new_tokens; // The maximum number of new tokens to generate.
  7: optional double repetition_penalty; // Penalty for repetition: >1 discourages repetition, <1 encourages it.
  8: optional double length_penalty; // Controls length of generated text. Values >1 encourage longer sequences, <1 shorter.
}

