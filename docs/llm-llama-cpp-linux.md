## Setup llm-inference using LLAMA-CPP 
This is a short guide to setup llm-inference project to run on your Linux machine using [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) package.

>`NOTE: Python 3.12 breaks torch instllation. Please use Python 3.10`

- **Create Python Virtual Environment:**
  - `python -m venv venv`


- **Activate the virtual environment:**
  - `source venv/bin/activate`
  - 

- **Install pytorch with cpu support**: 
  - `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`
  - llama-cpp-python guide: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/


- **Install Bitsandbytes**
  - `pip3 install bitsandbytes`


- Create `.env` file based on `.env.example` or `env-samples/env.llamacpp.example`
  - Change the Model path and config then Run the server:
    - `python3 main.py --multiprocess`

[Back to main doc](../README.md)