# llm-inference

Simple python code that can run inference on LLM models with rest api interface

# Prerequisites

Install cuda SDK: \
https://developer.nvidia.com/cuda-downloads \
Select your system config and how you want to install the SDK.

`NOTE: If you have 10xx series GPU you will require CUDA 11.8`

## Setup with local python

**Create Virtual Environment:**\
`python -m venv venv`

**Activate the virtual environment:** \
windows: `.\venv\Scripts\activate`\
Linux:`source venv/bin/activate`

**Install pytorch with cuda support**: \
https://pytorch.org/get-started/locally/ \
`NOTE: You may have to restart your IDE or the copmputer`

**Install required packages:** \
`pip install -r requirements.txt`

**Install transformers with cache support** \
`pip install git+https://github.com/huggingface/transformers.git`

**Install Bitsandbytes** \
Linux: `pip install bitsandbytes`
Windows: `pip install git+https://github.com/Keith-Hon/bitsandbytes-windows.git` \

Create `.env` file from `.env.example`\
and set the Model path then Run the server: \
`python server.py`

## Run with docker:

`docker run -d --gpus all -p 5000:5000 myapp` :TODO replace placeholder with docker image from dockerhub when done

## .env values and parameters

Default parameters:

```
SERVER_HOST = 127.0.0.1
SERVER_PORT = 5050
LOG_LEVEL = info

MODEL_PATH = /path/to/model 
ENABLE_CUDA = true
TARGET_GPU_INDEX = 0
ENABLE_USE_CACHE = true
LOW_CPU_MEM_USAGE = true
LOAD_IN_8BIT = false

MODEL_SEED = 42
MODEL_DEFAULT_NUM_BEAMS = 1
MODEL_DEFAULT_DO_SAMPLE = false
MODEL_DEFAULT_TEMPERATURE = 1.0
MODEL_DEFAULT_TOP_P = 1.0
MODEL_DEFAULT_TOP_K = 50

MODEL_DEFAULT_MAX_NEW_TOKENS = 4096
MODEL_DEFAULT_REPETITION_PENALTY = 1.0
MODEL_DEFAULT_LENGTH_PENALTY = 1.0
```

Rest API server config:

- **SERVER_HOST**:String - IP address the port will listen to (0.0.0.0 is any ip)
- **SERVER_PORT**:Int - Port the rest api service will listen to.
- **LOG_LEVEL**:String - Level of logs: critical, fatal, error, warning, warn, info, debug

General config:

- **MODEL_PATH**:String - Path to the model itself relative to the project.
- **ENABLE_CUDA**:Bool - Will try to run the model on the GPU if supported but will default to CPU if cuda is not
  supported.
- **TARGET_GPU_INDEX**:Int - Specify witch GPU to use to run the model when using LOW_CPU_MEM_USAGE set to true
    - Cuda SDK installation - https://developer.nvidia.com/cuda-zone
    - Only applicable when GPU is in use
- **ENABLE_USE_CACHE**:Bool - Weather or not to use caching for already calculated tokens, useful when pushing one token
  at a time
- **LOW_CPU_MEM_USAGE**:Bool - Exchange slower loading for less memory usage when loading the model
- **LOAD_IN_8BIT**:Bool - When true, loads the model in 8-bit precision instead of the standard 16-bit (
  bfloat16/float16), reducing RAM/GPU memory use but sacrificing some precision.

Default generation config:

- **MODEL_SEED**:Int - A seed in computing is a numerical value used to initialize a pseudorandom number generator,
  ensuring reproducibility of random sequences generated by the algorithm.
- **MODEL_DEFAULT_NUM_BEAMS**:Int- Number of different paths the model considers in parallel during beam search,
  influencing the diversity and quality of the generated text.
- **MODEL_DEFAULT_DO_SAMPLE**:Bool - Controls whether the model generates text by sampling from the probability
  distribution of each next word (when True), as opposed to just picking the most probable next word (when False).
- **MODEL_DEFAULT_TEMPERATURE**:Float - Hyperparameter that controls the randomness of predictions
- **MODEL_DEFAULT_TOP_P**:Float - Parameter used for nucleus sampling, controlling the randomness of output by only
  considering the smallest set of words whose cumulative probability exceeds the value p, thereby filtering out less
  likely words.
- **MODEL_DEFAULT_TOP_K**:Int - Parameter that limits the selection to the top k most probable next words, balancing the
  randomness and predictability of the generated text.

Default generation limits and penalties:

- **MODEL_DEFAULT_MAX_NEW_TOKENS**:Int - Max **new** tokens to generate per prompt request
- **MODEL_DEFAULT_REPETITION_PENALTY**:Float - Parameter used to discourage the model from repeating the same words or
  phrases, increasing the diversity of the generated text.
- **MODEL_DEFAULT_LENGTH_PENALTY**:Float - Parameter that adjusts the model's preference for longer or shorter
  sequences, with values greater than 1 favoring longer sequences and values less than 1 favoring shorter ones.

 