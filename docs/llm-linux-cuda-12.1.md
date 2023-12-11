## Setup Cuda SDK 12.1 or later ( GTX 20xx, 30xx, 40xx )
This is a short guide to setup llm-inference project to run on your Linux machine using latest CUDA drivers. \
This setup is viable if you have **Nvidia GTX 20xx series or later**.

- **Setup CUDA** \
Navigate to: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64 \
Select your Linux version and installation method follow the installation instructions.


- **Create Python Virtual Environment:**
  - `python -m venv venv`


- **Activate the virtual environment:**
  - `source venv/bin/activate`


- **Install pytorch with cuda support**: 
  - `pip3 install torch torchvision torchaudio`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`


- **Install transformers with cache support**
  - `pip3 install git+https://github.com/huggingface/transformers.git`


- **Install Bitsandbytes**
  - `pip3 install bitsandbytes`


- Create `.env` file based on `.env.example`
  - Change the Model path and config then Run the server:
    - `python3 server.py`

[Back to main doc](../README.md)
