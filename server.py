from flask import Flask, request, jsonify
from llm_model_handler import LLMModel
import config

model_config = {
    "ENABLE_CUDA": config.ENABLE_CUDA,
    "LOAD_IN_8BIT": config.LOAD_IN_8BIT,
    "LOW_CPU_MEM_USAGE": config.LOW_CPU_MEM_USAGE,
    "TARGET_GPU_INDEX": config.TARGET_GPU_INDEX,
    "MODEL_SEED": config.MODEL_SEED
}

llm_model = LLMModel(config.MODEL_PATH, model_config)
llm_model.load_model()
llm_model.run_model()


app = Flask(__name__)

if __name__ == "__main__":
    # DO NOT USE reloader, this ends up loading the model twice!
    app.run(debug=True, host=config.SERVER_HOST, port=config.SERVER_PORT, use_reloader=False)
