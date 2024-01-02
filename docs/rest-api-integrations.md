# Rest API Integrations

## /api/generate-one

Streaming JS example:

```js
const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify(postData), // Convert the JavaScript object to a JSON string
})
// Access stream reader
const reader = response.body.getReader()
while (true) {
    const {done, value} = await reader.read()
    if (done) break
    console.log(new TextDecoder().decode(value))
}
```

### Payload ( json )

```json
{
  "request_id": "YmFzZTY0",
  "prompt": "[INST] Generate a very long poem about 1000 cats [/INST]\n\n",
  "only_new_tokens": true,
  "stream_response": true,
  "generation_config": {
    "num_beams": 1,
    "do_sample": true,
    "temperature": 1,
    "top_p": 1,
    "top_k": 50,
    "max_new_tokens": 2048,
    "repetition_penalty": 1,
    "length_penalty": 1
  }
}
```

#### Payload explanations

| **Variable Name**     | **Default Value** | **values**  | **Description**                                                                                                      |
|-----------------------|-------------------|-------------|----------------------------------------------------------------------------------------------------------------------|
| **request_id**        | `required`        | Any String  | Unique ID of the request, also used for internal caching.                                                            |
| **prompt**            | `required`        | Any String  | Raw prompt for the model to use for generation. Will be ignored if cache exists (aka continue generation).           |
| **only_new_tokens**   | True (bool)       | True, False | Return only newly generated tokens when enabled; otherwise return the full sequence (including the original prompt). |
| **stream_response**   | True (bool)       | True, False | Whether or not to use HTTP Streaming when generating.                                                                |
| **generation_config** | from .env         | Object({})  | Configuration that affects the generation like temperature, length, etc.                                             |

#### Generation config explanations

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

### Response

- **Status:** 200
- **Type:** Text

```
Verse 1:
Their tails are feathers, like birds' wings.
They twirl, and dance, and skip across the lawn.
Their silky fur shimmers like diamonds.
```

## /api/generate-batch

### Payload ( json )

```json
{
  "prompts": [
    {
      "request_id": "YmFzZTY0",
      "prompt": "[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
    },
    {
      "request_id": "rFERfgE",
      "prompt": "[INST] Generate a short poem about 1000 dogs [/INST]\n\n"
    }
  ],
  "only_new_tokens": false,
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

#### Payload explanations

| **Variable Name**     | **Default Value** | **values**          | **Description**                                                                                                      |
|-----------------------|-------------------|---------------------|----------------------------------------------------------------------------------------------------------------------|
| **only_new_tokens**   | True (bool)       | True, False         | Return only newly generated tokens when enabled; otherwise return the full sequence (including the original prompt). |
| **prompts**           | `required`        | Array of Object({}) | Array of objects that specify the individual prompts for batch generation.                                           |
| **generation_config** | from .env         | Object({})          | Configuration that affects the generation like temperature, length, etc.                                             |

#### Payload prompts explanations

| **Variable Name** | **Default Value** | **values** | **Description**                                                                                             |
|-------------------|-------------------|------------|-------------------------------------------------------------------------------------------------------------|
| **request_id**    | `required`        | Any String | Unique ID of the request, also used for internal caching                                                    |
| **prompt**        | `required`        | Any String | Raw prompt for the model to use for generation. `Will be ignored if cache exists (aka continue generation)` |

`Note: due to the nature of caching, different order of prompts will produce differet caching key`

#### Generation config explanations

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

### Responses

`only_new_tokens: false`

```json
[
  {
    "request_id": "YmFzZTY0",
    "prompt": "<s> [INST] Generate a very long poem about 1000 cats [/INST]\n\n",
    "response": "In the land of feline delight,\nWhere..."
  },
  {
    "request_id": "rFERfgE",
    "prompt": "<s> [INST] Generate a short poem about 1000 dogs [/INST]\n\n",
    "response": "Tails wagging, eyes bright,\n..."
  }
]
```

`only_new_tokens: true`

```json
[
  {
    "request_id": "YmFzZTY0",
    "response": "In the land of feline delight,\nWhere..."
  },
  {
    "request_id": "rFERfgE",
    "response": "Tails wagging, eyes bright,\n..."
  }
]
```

#### Response Array explanations

| **Variable Name** | **Type**         | **values** | **Description**                                                                                  |
|-------------------|------------------|------------|--------------------------------------------------------------------------------------------------|
| **request_id**    | String           | Any String | Unique ID of the request, also used for internal caching.                                        |
| **prompt**        | Optional(String) | Any String | Raw prompt for the model to use for generation. Will not be returned if only_new_tokens is true. |
| **response**      | String           | Any String | Text generated by the model.                                                                     |

[Back to main doc](../README.md)