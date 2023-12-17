## Setup llm-inference using CPU on windows
This is a short guide to setup llm-inference project to run on your Linux machine using CPU.

- **Create Python Virtual Environment:**
  - `python -m venv venv`


- **Activate the virtual environment:**
  - `source venv/bin/activate`
  - 

- **Install pytorch with cuda support**: 
  - `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`


- **Install transformers with cache support** 
  - `pip3 install git+https://github.com/huggingface/transformers.git`


- **Install Bitsandbytes**
  - `pip3 install bitsandbytes`


- Create `.env` file based on `.env.example`
  - Change the Model path and config then Run the server:
    - `python3 main.py --multiprocess`

[Back to main doc](../README.md)