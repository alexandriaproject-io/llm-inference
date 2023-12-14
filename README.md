# llm-inference

Simple python code that can run inference on LLM models with rest api interface.

- [Setup and run locally](#run-with-locally)
    - [Resource requirements](docs/usage.md)
- [Run with Docker](#run-with-docker)
- [Configuration values and parameters](#env-values-and-parameters)
    - [Rest API server config](#rest-api-server-config)
    - [General config](#general-config)
    - [Generation config](#default-generation-config)
    - [Generation limits config](#default-generation-limits-and-penalties)

Want to know how this service works?
- [LLM Service **Architecture**](docs/architecture.md)
- [LLM Service **Rest API** UML](docs/rest-api-uml.md)
- [LLM Service **WebSocket** UML](docs/websocket-uml.md)

## Run with locally

Due to the variety of setups and the fact that each one requires different versions of PyTorch. \
Before we head out here is a list of system Memory and GPU requirements.

- [Resource requirements can be found here](docs/usage.md)

**Setup Windows locally**

- [Cuda 12.1 or later ( GTX 20xx, 30xx, 40xx )](docs/llm-windows-cuda-12.1.md)
- [Cuda 11.8 ( for GTX 10xx series)](docs/llm-windows-cuda-11.8.md)
- [CPU - slow but reliable](docs/llm-windows-cpu.md)

**Setup Linux locally**

- [Cuda 12.1 or later ( GTX 20xx, 30xx, 40xx )](docs/llm-linux-cuda-12.1.md)
- [Cuda 11.8 ( for GTX 10xx series)](docs/llm-linux-cuda-11.8.md)
- [CPU - slow but reliable](docs/llm-linux-cpu.md)

## Run with docker

- **CPU Mode**
    - CPU - slow but reliable
        - ```
            docker run --name alexandria-project alexandria-project -v path/to/model:/usr/model --env-file https://raw.githubusercontent.com/alexandriaproject-io/llm-inference/main/env-samples/.env.cpu.example 
          ```

- **CUDA Mode**
    - Verify docker access:
        - ```
            docker run --gpus all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark
            ```
            - If not please
              install https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html


- **Cuda 12.1 or later ( GTX 20xx, 30xx, 40xx )**
    - ```
      docker run --gpus all --name alexandria-project alexandria-project -v path/to/model:/usr/model --env-file https://raw.githubusercontent.com/alexandriaproject-io/llm-inference/main/env-samples/.env.cuda.example 
      ```
- **Cuda 11.8 ( for GTX 10xx series)**
    - ```
      docker run --gpus all --name alexandria-project alexandria-project -v path/to/model:/usr/model --env-file https://raw.githubusercontent.com/alexandriaproject-io/llm-inference/main/env-samples/.env.cuda.example 
      ```

## .env values and parameters

You can find the example file here [.env.example](.env.example)

### Rest API server config:

| **Variable Name** | **Default Value** | **values**                                         | **Description**                                                   |
|-------------------|-------------------|----------------------------------------------------|-------------------------------------------------------------------|
| **SERVER_HOST**   | 127.0.0.1         | 0.0.0.0 - 255.255.255.255                          | IP address the port will listen to (0.0.0.0 is any ip).           |
| **SERVER_PORT**   | 5050              | 1-65535                                            | Port the rest api service will listen to.                         |
| **LOG_LEVEL**     | info              | critical, fatal, error, warning, warn, info, debug | Level of logs: critical, fatal, error, warning, warn, info, debug |

### General config:

| **Variable Name**     | **Default Value** | **values**                    | **Description**                                                                                                                                                             |
|-----------------------|-------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **MODEL_PATH**        | -                 | relative/path/to/model/folder | Path to the model itself relative to the project.                                                                                                                           |
| **ENABLE_CUDA**       | true              | true, false                   | Will try to run the model on the GPU if supported but will default to CPU if cuda is not supported.                                                                         |
| **TARGET_GPU_INDEX**  | 0                 | Any Int                       | Specify witch GPU to use to run the model when using LOW_CPU_MEM_USAGE set to true.<br/>Only applicable when GPU is in use                                                  |
| **LOW_CPU_MEM_USAGE** | true              | true, false                   | Exchange slower loading for less memory usage when loading the model                                                                                                        |
| **LOAD_IN_8BIT**      | false             | true, false                   | When true, loads the model in 8-bit precision instead of the standard 16-bit (bfloat16/float16), reducing RAM/GPU memory use but sacrificing some precision.                |
| **LOAD_IN_4BIT**      | false             | true, false                   | **LINUX ONLY** When true, loads the model in 4-bit precision instead of the standard 16-bit (bfloat16/float16), reducing RAM/GPU memory use but sacrificing some precision. |

### Default generation config:

| **Variable Name**             | **Default Value** | **values**   | **Description**                                                                                                                                                                                                    |
|-------------------------------|-------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **MODEL_SEED**                | 42                | 0-2147483647 | A seed in computing is a numerical value used to initialize a pseudorandom number generator ensuring reproducibility of random sequences generated by the algorithm.                                               |
| **MODEL_DEFAULT_NUM_BEAMS**   | 1                 | Any Int      | Number of different paths the model considers in parallel during beam search, influencing the diversity and quality of the generated text.                                                                         |
| **MODEL_DEFAULT_DO_SAMPLE**   | false             | true, false  | Controls whether the model generates text by sampling from the probability distribution of each next word (when True), as opposed to just picking the most probable next word (when False).                        |
| **MODEL_DEFAULT_TEMPERATURE** | 1.0               | Any Float    | Hyperparameter that controls the randomness of predictions, the higher the more random.                                                                                                                            |
| **MODEL_DEFAULT_TOP_P**       | 1.0               | Any Float    | Parameter used for nucleus sampling, controlling the randomness of output by only considering the smallest set of words whose cumulative probability exceeds the value p, thereby filtering out less likely words. |
| **MODEL_DEFAULT_TOP_K**       | 50                | Any Int      | Parameter that limits the selection to the top k most probable next words, balancing the randomness and predictability of the generated text.                                                                      |

### Default generation limits and penalties:

| **Variable Name**                    | **Default Value** | **values** | **Description**                                                                                                                                                                   |
|--------------------------------------|-------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **MODEL_DEFAULT_MAX_NEW_TOKENS**     | 2096              | Any Int    | Max **new** tokens to generate per prompt request depending on the model capabilites.                                                                                             |
| **MODEL_DEFAULT_REPETITION_PENALTY** | 1                 | Any Float  | Parameter used to discourage the model from repeating the same words or phrases, increasing the diversity of the generated text.                                                  |
| **MODEL_DEFAULT_LENGTH_PENALTY**     | 1                 | Any Float  | Parameter that adjusts the model's preference for longer or shorter sequences, with values greater than 1 favoring longer sequences and values less than 1 favoring shorter ones. |



 

 