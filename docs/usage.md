# Example of system requirements for LLama-2-7B

Here are the requirements for LLama-2-7B ( the small LLM from Meta ). \
These are measured on`Ryzen 5800x 128GB DDR4(3200MHz) - GTX 4090 using CUDA 12.3`.\
They only capture the idle usage that the inference will require.

**NOTE: When running in 8Bit or 4Bit install CUDA version on Linux.** \
**Bitsandbytes require GPU to quantize the model**

### CPU Inference Mode resources usage with LLAMA2 7B - **Idle**

| **CPU Mode**       | **CPU Ram** | **GPU Ram** | Tokens / Second | Support              |
|--------------------|-------------|-------------|-----------------|----------------------|
| **Float32**        | 28GB        | -           | ~ 1 tok / sec   | Linux and Windows    |
| **BF16 / Float16** | -           | -           | -               | Not supported on CPU |
| **Float8 / 8Bit**  |             | -           | -               | Not supported on CPU |
| **Float4 / 4Bit**  |             | -           | -               | Not supported on CPU | 

 `Note: quanitization requires GPU to run the model compression install Cuda version to run quanitized on CPU.` \
A good alternative is to use https://github.com/ggerganov/llama.cpp instead. \
A guide we found for Windows: https://github.com/mpwang/llama-cpp-windows-guide


### GPU Inference Mode resources usage with LLAMA2 7B - **Idle** 

| Cuda Mode          | CPU | Cuda mode | Tokens / Second         | Support                |
|--------------------|-----|-----------|-------------------------|------------------------|
| **Float32**        | -   | -         | Not implemented ( TBD ) | Linux and Windows      |  
| **BF16 / Float16** | 3GB | 14GB      | ~ 45 tok / sec          | Linux and Windows      |
| **Float8 / 8Bit**  | 3GB | 9GB       | ~ 7 tok / sec           | Linux and Windows      |
| **Float4 / 4Bit**  | 3GB | 6GB       | ~ 30 tok / sec          | Linux only |

- `Note: 8/4 Bit quanitization requires GPU to run the model compression install Cuda version to run quanitized on CPU`
- `Note: using bits and bytes for windows only works with cudal 11.8 atm`

[Back to main doc](../README.md)