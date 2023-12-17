## Setup Cuda SDK 12.1 or later ( GTX 20xx, 30xx, 40xx )
This is a short guide to setup llm-inference project to run on your Windows machine using latest CUDA drivers. \
This setup is viable if you have **Nvidia GTX 20xx series or later**.

- **Setup CUDA** \
Navigate to: https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64 \
Select your Windows version and installation method then install.

 
- **Create Python Virtual Environment:**\
`python -m venv venv`


- **Activate the virtual environment:** \
 `.\venv\Scripts\activate`


- **Install pytorch with cuda support**: \
  - `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
    - source: https://pytorch.org/get-started/locally/ 
   

- **Install required packages:** 
  - `pip3 install -r requirements.txt`


- **Install transformers with cache support** 
  - `pip3 install git+https://github.com/huggingface/transformers.git`


- **Install Bitsandbytes** - windows compatible version 
  - `pip3 install git+https://github.com/Keith-Hon/bitsandbytes-windows.git`


- Create `.env` file based on `.env.example`
  - Change the Model path and config then Run the server:
    - `python main.py --multiprocess`

[Back to main doc](../README.md)
