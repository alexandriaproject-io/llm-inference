# llm-inference

Simple python code that can run inference on LLM models with rest api interface.

- [Setup and run locally](#run-with-locally)
    - [Resource requirements](docs/usage.md)
- [Docker images](#docker-images)
- [Run with Docker](#run-with-docker)
    - [Docker images](#docker-images)
    - [Docker examples](#docker-examples)
        - [Run with huggingface model](#run-with-huggingface-model)
        - [Run with local model](#run-with-local-model)
        - [Run with custom env-file](#run-with-custom-env-file)
- [Docker build](#docker-build)
- [Configuration values and parameters](#env-values-and-parameters)
    - [Rest API server config](#rest-api-server-config)
    - [General config](#general-config)
    - [Generation config](#default-generation-config)
    - [Generation limits config](#default-generation-limits-and-penalties)

Want to know how this service works?

- [LLM Service **Architecture**](docs/architecture.md)
- [LLM Service **Rest API** UML](docs/rest-api-uml.md)
    - [Rest API integration docs](docs/rest-api-integrations.md)
- [LLM Service **WebSocket** UML](docs/websocket-uml.md)
    - [WebSocket integration docs](docs/ws-integrations.md)

Want to use the service in your project:

- [Rest API integration docs](docs/rest-api-integrations.md)
- [WebSocket integration docs](docs/ws-integrations.md)

## Run with locally

Due to the variety of setups and the fact that each one requires different versions of PyTorch. \
Before we head out here is a list of system Memory and GPU requirements.

> `NOTE: Python 3.12 breaks torch instllation. Please use Python 3.10`

- [Resource requirements can be found here](docs/usage.md)

**Setup Windows locally**

- [Cuda 12.1 or later ( GTX 20xx, 30xx, 40xx )](docs/llm-windows-cuda-12.1.md)
- [Cuda 11.8 ( for GTX 10xx series)](docs/llm-windows-cuda-11.8.md)
- [CPU - slow but reliable](docs/llm-windows-cpu.md)

```
NOTE: if you get error:
... exit code -1073741819 (0xC0000005)
you need to add PYTHONUNBUFFERED=1;PYDEVD_USE_FRAME_EVAL=NO to your Run/Debug env variables
```

**Setup Linux locally**

- [Cuda 12.1 or later ( GTX 20xx, 30xx, 40xx )](docs/llm-linux-cuda-12.1.md)
- [Cuda 11.8 ( for GTX 10xx series)](docs/llm-linux-cuda-11.8.md)
- [CPU - slow but reliable](docs/llm-linux-cpu.md)

**Use llama-cpp-python package**

- **Windows**: [LLAMA-CPP-Windows - low-end hardware](docs/llm-llama-cpp-windows.md)
- **Linux**: [LLAMA-CPP-Linux - low-end hardware](docs/llm-llama-cpp-linux.md)

`Note: You will need to aquire GGUF model.`

- For example:
    - **docs:**
      [TheBloke/Mistral-7B-Instruct-v0.2-GGUF](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)
    - **files:**
      [TheBloke/Mistral-7B-Instruct-v0.2-GGUF/tree/main](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/tree/main)

## Run with docker

- **CUDA Mode** - using cuda required cuda drivers and cuda docker support.
    - requirements:
        - nvidia-drivers (instruction in the sections above according to your os)
        - [cuda](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64)
        - [docker-nvida2](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
    - Verify docker access:
        - `docker run --gpus all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark`

## Docker images

**Images:**

- `niftylius/llm-inference:auto` / `niftylius/llm-inference:latest`
    - Will use the `auto` flag when loading the model,it will prioritize GPU but spread the model on cpu if there is
      not enough VRAM available.
- `niftylius/llm-inference:cpu`
    - Will use the `cpu` flag when loading the model, this will load the model to RAM and use CPU for inference
- `niftylius/llm-inference:cuda-11`
    - For older GPUS. Will use the `cuda` flag and cuda-11.8 drivers when loading the model. Peripherally for 10xx
      nvidia GPUs.
- `niftylius/llm-inference:cuda-12`
    - Will use the `cuda` flag and cuda-12.1 drivers when loading the model.
- `niftylius/llm-inference:llama-cpp`
    - Will use llama-cpp as the inference service instead of Huggingface transformers.
    - `NOTE: cpu mode only if you want to run quantized version use LOAD_IN_4BIT flag on "auto" or "cuda" dockers`

## Docker examples

Load TinyLlama/TinyLlama-1.1B-Chat-v1.0 using default settings

```shell
# auto
docker run --gpus all -e MODEL_PATH="TinyLlama/TinyLlama-1.1B-Chat-v1.0" -p 6060:6060 niftylius/llm-inference:auto

# cuda 12.1
docker run --gpus all -e MODEL_PATH="TinyLlama/TinyLlama-1.1B-Chat-v1.0" -p 6060:6060 niftylius/llm-inference:cuda-12

# cuda 11.8
docker run --gpus all -e MODEL_PATH="TinyLlama/TinyLlama-1.1B-Chat-v1.0" -p 6060:6060 niftylius/llm-inference:cuda-11

# cpu
docker run -e MODEL_PATH="TinyLlama/TinyLlama-1.1B-Chat-v1.0" -p 6060:6060 niftylius/llm-inference:cpu

# llama-cpp on cpu
docker run -v [path/to/some_model_folder]:/usr/model -e MODEL_PATH="/usr/model/[your model].gguf" -p 6060:6060 niftylius/llm-inference:llama-cpp
```

### Run with huggingface model

```shell
# auto
docker run --gpus all -e MODEL_PATH="[huggingface model url]" -p 6060:6060 niftylius/llm-inference

# example1: docker run --gpus all -e MODEL_PATH="TinyLlama/TinyLlama-1.1B-Chat-v1.0" -p 6060:6060 niftylius/llm-inference
# example2: docker run --gpus all -e MODEL_PATH="mistralai/Mistral-7B-Instruct-v0.2" -p 6060:6060 niftylius/llm-inference
```

### Run with local model

Make sure the path to your model is absolute

```shell
# this will load the model from your local machine
docker run --gpus all -p 6060:6060 -v path/to/some_model:/usr/model niftylius/llm-inference:latest
```

### Run with custom env-file

Download .env.example file locally from: \
https://raw.githubusercontent.com/alexandriaproject-io/llm-inference/main/.env.example

```shell
# edit .env.example and run
docker run --gpus all --env-file .env.example -e MODEL_PATH="[huggingface model url]" -p 6060:6060 niftylius/llm-inference:latest
```

## Docker build

Clone git project with: \
`git clone git@github.com:alexandriaproject-io/llm-inference.git`

Navigate in to the project folder and run:

```shell
# build auto docker image
docker build -f .\docker\Dockerfile.auto -t [Your Image tag name] .

# build cuda 12.1 docker image
docker build -f .\docker\Dockerfile.cuda12 -t [Your Image tag name] .

# build cuda 11.8 docker image
docker build -f .\docker\Dockerfile.cuda11 -t [Your Image tag name] .

# build cpu docker image
docker build -f .\docker\Dockerfile.cpu -t [Your Image tag name] .

# build llama-cpp
docker build -f .\docker\Dockerfile.llama-cpp.cuda -t [Your Image tag name] .
```

## .env values and parameters

You can find the example file here [.env.example](.env.example)

### Rest API server config:

| **Variable Name**  | **Default Value** | **values**                                         | **Description**                                                                                                                                                 |
|--------------------|-------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **SERVER_HOST**    | 127.0.0.1         | 0.0.0.0 - 255.255.255.255                          | IP address the port will listen to (0.0.0.0 is any ip).                                                                                                         |
| **SERVER_PORT**    | 6060              | 1-65535                                            | Port the rest api service will listen to.                                                                                                                       |
| **LOG_LEVEL**      | info              | critical, fatal, error, warning, warn, info, debug | Level of logs: critical, fatal, error, warning, warn, info, debug                                                                                               |
| **MAX_CACHE_SIZE** | 16384             | 1-2147483647                                       | Max cached prompt executions                                                                                                                                    |
| **MAX_CACHE_TTL**  | 3600              | 1-2147483647                                       | **Cache TTL** - after this time from the last **request_id/request_ids** execution the cache will be cleared. Cache is also **cleared** with **EOS** is reached |

### General config:

| **Variable Name** | **Default Value** | **values**                    | **Description**                                   |
|-------------------|-------------------|-------------------------------|---------------------------------------------------|
| **MODEL_PATH**    | -                 | relative/path/to/model/folder | Path to the model itself relative to the project. |

### LLama.cpp config ( used for integration/debugging )

| **Variable Name**          | **Default Value** | **values**  | **Description**                                                                                                  |
|----------------------------|-------------------|-------------|------------------------------------------------------------------------------------------------------------------|
| **USE_LLAMA_CPP**          | false             | true, false | Weather to use [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) package to run GGUL models on CPU |
| **LLAMA_CPP_MAX_CONTEXT**  | 2048              | Any Int     | The maximum prompt and response size is set manually because it's not defined in the GGUL models.                |
| **LLAMA_CPP_BATCH_TOKENS** | 2048              | Any Int     | Represents the number of batches or the size of each batch being processed in the program.                       |
| **LLAMA_RAM_CACHE_MB**     | 512               | Any Int     | Caching greatly increases repeated prompt generations ( like 10 tokes at a time )                                |

`NOTE: when using llama-cpp all of the **Transformers config** will be ignored` \
`NOTE: this is used primeraly for debugging its not a good implementation of llama.cpp`

### Huggingface Transformers config

| **Variable Name**    | **Default Value** | **values**  | **Description**                                                                                                                                                             |
|----------------------|-------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ENABLE_CUDA**      | true              | true, false | Will try to run the model on the GPU if supported but will default to CPU if cuda is not supported.                                                                         |
| **DEVICE_MAP_AUTO**  | false             | true, false | Will automatically space the model on all GPUs and the CPU. TARGET_GPU_INDEX will be ignored when set to True                                                               |
| **TARGET_GPU_INDEX** | 0                 | Any Int     | Specify witch GPU to use to run the model on.<br/>Only applicable when GPU is in use                                                                                        |
| **LOAD_IN_8BIT**     | false             | true, false | When true, loads the model in 8-bit precision instead of the standard 16-bit (bfloat16/float16), reducing RAM/GPU memory use but sacrificing some precision.                |
| **LOAD_IN_4BIT**     | false             | true, false | **LINUX ONLY** When true, loads the model in 4-bit precision instead of the standard 16-bit (bfloat16/float16), reducing RAM/GPU memory use but sacrificing some precision. |
| **SPACE_TOKEN_CHAR** | ▁                 | String      | Some models like LLama 2 remove leading space when decoding token by token, define this token to try and fix that behaviour on PROGRESS events                              |

### Default generation config:`

| **Variable Name**             | **Default Value**    | **values**   | **Description**                                                                                                                                                                                                    |
|-------------------------------|----------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **MODEL_SEED**                | 42                   | 0-2147483647 | A seed in computing is a numerical value used to initialize a pseudorandom number generator ensuring reproducibility of random sequences generated by the algorithm.                                               |
| **MODEL_LOADER**              | AutoModelForCausalLM | String       | Manually set Model class ( for debugging and experimentation ). Models mapping can be found [here](https://huggingface.co/transformers/v4.11.3/_modules/transformers/models/auto/modeling_auto.html)               |
| **MODEL_DEFAULT_NUM_BEAMS**   | 1                    | Any Int      | Number of different paths the model considers in parallel during beam search, influencing the diversity and quality of the generated text.                                                                         |
| **MODEL_DEFAULT_DO_SAMPLE**   | true                 | true, false  | Controls whether the model generates text by sampling from the probability distribution of each next word (when True), as opposed to just picking the most probable next word (when False).                        |
| **MODEL_DEFAULT_TEMPERATURE** | 1.0                  | Any Float    | Hyperparameter that controls the randomness of predictions, the higher the more random.                                                                                                                            |
| **MODEL_DEFAULT_TOP_P**       | 1.0                  | Any Float    | Parameter used for nucleus sampling, controlling the randomness of output by only considering the smallest set of words whose cumulative probability exceeds the value p, thereby filtering out less likely words. |
| **MODEL_DEFAULT_TOP_K**       | 50                   | Any Int      | Parameter that limits the selection to the top k most probable next words, balancing the randomness and predictability of the generated text.                                                                      |

### Default generation limits and penalties:

| **Variable Name**                    | **Default Value** | **values** | **Description**                                                                                                                                                                   |
|--------------------------------------|-------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **MODEL_DEFAULT_MAX_NEW_TOKENS**     | 2048              | Any Int    | Max **new** tokens to generate per prompt request depending on the model capabilites.                                                                                             |
| **MODEL_DEFAULT_REPETITION_PENALTY** | 1                 | Any Float  | Parameter used to discourage the model from repeating the same words or phrases, increasing the diversity of the generated text.                                                  |
| **MODEL_DEFAULT_LENGTH_PENALTY**     | 1                 | Any Float  | Parameter that adjusts the model's preference for longer or shorter sequences, with values greater than 1 favoring longer sequences and values less than 1 favoring shorter ones. |

## resources

https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
https://github.com/coreui/coreui-free-react-admin-template
 

 