## Setup Cuda SDK 11.8 legacy ( GTX 10xx )
This is a short guide to setup llm-inference project to run on your Linux machine using legacy CUDA drivers. \
This setup is viable if you have **Nvidia GTX 10xx** series.

>`NOTE: Python 3.12 breaks torch instllation. Please use Python 3.10`

- **Setup CUDA** \
Navigate to: https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Linux&target_arch=x86_64 \
Select your Linux version and installation method follow the installation instructions.


 
- **Create Python Virtual Environment:**
  - `python -m venv venv`


- **Activate the virtual environment:**
  - `source venv/bin/activate`


- **Install pytorch with cuda support**: 
  - `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`
  - llama-cpp-python guide: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/

- **Install Bitsandbytes**
  - `pip3 install bitsandbytes`


- Create `.env` file based on `.env.example` or `env-samples/env.cuda.example`
  - Change the Model path and config then Run the server:
    - `python3 main.py --multiprocess`

[Back to main doc](../README.md)