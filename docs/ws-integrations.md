# WebSocket Integrations ( /ws )

- [**Payload structure**](#queue-generation-payload)
    - [**Prompts structure**](#prompts)
    - [**Generation config structure**](#generationconfig)
- [**Service Response Events**](#service-response-events)
    - [**ACCEPTED**](#type-accepted)
    - [**STARTED**](#type-started)
    - [**INITIALIZED**](#type-initialized)
    - [**PROGRESS**](#type-progress)
    - [**COMPLETE**](#type-complete)
    - [**ERROR**](#type-error)

## Queue generation payload

```json
{
  "prompts": [
    {
      "request_id": "2835f3c5",
      "prompt": "[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
    }
  ],
  "only_new_tokens": true,
  "stream_response": true,
  "generation_config": {
    "num_beams": 1,
    "do_sample": true,
    "temperature": 1,
    "top_p": 1,
    "top_k": 50,
    "max_new_tokens": 100,
    "repetition_penalty": 1,
    "length_penalty": 1
  }
}
```

| **Variable Name**     | **Default Value** | **values**          | **Description**                                                                                                      |
|-----------------------|-------------------|---------------------|----------------------------------------------------------------------------------------------------------------------|
| **only_new_tokens**   | True (bool)       | True, False         | Return only newly generated tokens when enabled; otherwise return the full sequence (including the original prompt). |
| **prompts**           | `required`        | Array of Object({}) | Array of objects that specify the individual prompts for batch generation.                                           |
| **generation_config** | from .env         | Object({})          | Configuration that affects the generation like temperature, length, etc.                                             |

### prompts

| **Variable Name** | **Default Value** | **values** | **Description**                                                                                             |
|-------------------|-------------------|------------|-------------------------------------------------------------------------------------------------------------|
| **request_id**    | `required`        | Any String | Unique ID of the request, also used for internal caching                                                    |
| **prompt**        | `required`        | Any String | Raw prompt for the model to use for generation. `Will be ignored if cache exists (aka continue generation)` |

`Note: due to the nature of caching, different order of prompts will produce differet caching key`

### generation_config

| **Variable Name**      | **Default Value** | **values**  | **Description**                                                                                                                                                                                                    |
|------------------------|-------------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **num_beams**          | Int from .env     | Any Int     | Number of different paths the model considers in parallel during beam search, influencing the diversity and quality of the generated text.                                                                         |
| **do_sample**          | Bool from .env    | true, false | Controls whether the model generates text by sampling from the probability distribution of each next word (when True), as opposed to just picking the most probable next word (when False).                        |
| **temperature**        | Float from .env   | Any Float   | Hyperparameter that controls the randomness of predictions, the higher the more random.                                                                                                                            |
| **top_p**              | Float from .env   | Any Float   | Parameter used for nucleus sampling, controlling the randomness of output by only considering the smallest set of words whose cumulative probability exceeds the value p, thereby filtering out less likely words. |
| **top_k**              | Int from .env     | Any Int     | Parameter that limits the selection to the top k most probable next words, balancing the randomness and predictability of the generated text.                                                                      |
| **max_new_tokens**     | Int from .env     | Any Int     | Max **new** tokens to generate per prompt request depending on the model capabilites.                                                                                                                              |
| **repetition_penalty** | Float from .env   | Any Float   | Parameter used to discourage the model from repeating the same words or phrases, increasing the diversity of the generated text.                                                                                   |
| **length_penalty**     | Float from .env   | Any Float   | Parameter that adjusts the model's preference for longer or shorter sequences, with values greater than 1 favoring longer sequences and values less than 1 favoring shorter ones.                                  |

## Service Response Events

Event types:

- [**ACCEPTED**](#type-accepted): Request passed validation and is now queued for execution
- [**STARTED**](#type-started): Request was picked up by the model and is now being loaded
- [**INITIALIZED**](#type-initialized): Request was loaded into the model and is now generating new tokens
- [**PROGRESS**](#type-progress):If streaming is enabled, it will contain the next generated token.
- [**COMPLETE**](#type-complete):Summary event when generation is complete.
- [**ERROR**](#type-error):Error event during text generation.

### Type ACCEPTED

Request passed validation and is now queued for execution

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "2835f3c5",
    "type": "ACCEPTED"
  },
  ...
]
```

| **Variable Name** | **Value**        | **Description**               |
|-------------------|------------------|-------------------------------|
| **request_id**    | String           | Id of the original request id |
| **type**          | ENUM['ACCEPTED'] | Type of the event             |

### Type STARTED

Request was picked up by the model and is now being loaded

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "2835f3c5",
    "type": "STARTED"
  },
  ...
]
```

| **Variable Name** | **Value**       | **Description**               |
|-------------------|-----------------|-------------------------------|
| **request_id**    | String          | Id of the original request id |
| **type**          | ENUM['STARTED'] | Type of the event             |

### Type INITIALIZED

Request was loaded into the model and is now generating new tokens

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "2835f3c5",
    "type": "INITIALIZED",
    "text": "[INST] Lorem Impsum..."
  },
  ...
]
```

| **Variable Name** | **Value**           | **Description**                                                         |
|-------------------|---------------------|-------------------------------------------------------------------------|
| **request_id**    | String              | Id of the original request id                                           |
| **type**          | ENUM['INITIALIZED'] | Type of the event                                                       |
| **text**          | String              | Empty string if `only_new_tokens:true`. Otherwise initial prompt string |

### Type PROGRESS

If streaming is enabled, it will contain the next generated token.

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "2835f3c5",
    "type": "PROGRESS",
    "text": "The"
  },
  ...
]
```

| **Variable Name** | **Value**        | **Description**                         |
|-------------------|------------------|-----------------------------------------|
| **request_id**    | String           | Id of the original request id           |
| **type**          | ENUM['PROGRESS'] | Type of the event                       |
| **text**          | String           | The newly generated token's text value. |

### Type COMPLETE

Summary event when generation is complete.

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "2835f3c5",
    "type": "COMPLETE",
    "text": "In the land of cats...",
    "is_eos": false,
    "new_tokens_count": 100,
    "execution_time": 1.711
  },
  ...
]
```

| **Variable Name**    | **Value**        | **Description**                                                                                      |
|----------------------|------------------|------------------------------------------------------------------------------------------------------|
| **request_id**       | String           | ID of the original request.                                                                          |
| **type**             | ENUM['COMPLETE'] | Type of the event.                                                                                   |
| **text**             | String           | Full text generated (with or without the initial prompt, based on the `only_new_tokens` value).      |
| **is_eos**           | Bool             | Indicates whether the End of Sentence (EOS) token has been generated, signaling the end of the text. |
| **new_tokens_count** | Int              | Number of newly generated tokens.                                                                    |
| **execution_time**   | Float            | Total time taken for generation, measured in seconds.                                                |

### Type ERROR

Error event during text generation.

```json
// Returns array of events for batch ( equivalent to prompts array )
[
  {
    "request_id": "9099dc5e",
    "type": "ERROR",
    "error": "`streamer` cannot be used with beam search (yet!). Make sure that `num_beams` is set to 1."
  },
  ...
]
```

| **Variable Name** | **Value**     | **Description**               |
|-------------------|---------------|-------------------------------|
| **request_id**    | String        | Id of the original request id |
| **type**          | ENUM['ERROR'] | Type of the event             |
| **error**         | String        | Error text                    |



[Back to main doc](../README.md)

