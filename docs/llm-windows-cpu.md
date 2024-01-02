## Setup llm-inference using CPU on windows
This is a short guide to setup llm-inference project to run on your Windows machine using CPU.

>`NOTE: Python 3.12 breaks torch instllation. Please use Python 3.10`

- **Install Windows build tools from:** \
https://visualstudio.microsoft.com/visual-cpp-build-tools/ \
You are looking for **Desktop Development with C++**
 

- **Create Python Virtual Environment:**
  - `python -m venv venv`


- **Activate the virtual environment:** 
  - `.\venv\Scripts\activate`


- **Install pytorch with cpu support**: 
  - `pip3 install torch torchvision torchaudio`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`
  - llama-cpp-python guide: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/


- **Install Bitsandbytes** - windows compatible version 
  - `pip3 install git+https://github.com/Keith-Hon/bitsandbytes-windows.git`


- Create `.env` file based on `.env.example` or `env-samples/env.cpu.example`
  - Change the Model path and config then Run the server:
    - `python main.py --multiprocess`

[Back to main doc](../README.md)