from dotenv import load_dotenv
import os

load_dotenv()

# Rest API server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5050"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "16384"))
MAX_CACHE_TTL = int(os.getenv("MAX_CACHE_TTL", "3600"))

# Model inference configuration
MODEL_PATH = os.getenv("MODEL_PATH")
ENABLE_CUDA = os.getenv("ENABLE_CUDA", "true").lower() == 'true'
TARGET_GPU_INDEX = int(os.getenv("TARGET_GPU_INDEX", "0"))
LOW_CPU_MEM_USAGE = os.getenv("LOW_CPU_MEM_USAGE", "False").lower() == 'true'
LOAD_IN_8BIT = os.getenv("LOAD_IN_8BIT", "False").lower() == 'true'
LOAD_IN_4BIT = os.getenv("LOAD_IN_4BIT", "False").lower() == 'true'

# Token generation configuration
MODEL_SEED = int(os.getenv("MODEL_SEED", "42"))
MODEL_DEFAULT_NUM_BEAMS = int(os.getenv("MODEL_DEFAULT_NUM_BEAMS", "1"))
MODEL_DEFAULT_DO_SAMPLE = os.getenv("MODEL_DEFAULT_DO_SAMPLE", "False").lower() == 'true'
MODEL_DEFAULT_TEMPERATURE = float(os.getenv("MODEL_DEFAULT_TEMPERATURE", "1"))
MODEL_DEFAULT_TOP_P = float(os.getenv("MODEL_DEFAULT_TOP_P", "1"))
MODEL_DEFAULT_TOP_K = int(os.getenv("MODEL_DEFAULT_TOP_K", "50"))

# Token generation penalties and limitations
MODEL_DEFAULT_MAX_NEW_TOKENS = int(os.getenv("MODEL_DEFAULT_MAX_NEW_TOKENS", "4096"))
MODEL_DEFAULT_REPETITION_PENALTY = float(os.getenv("MODEL_DEFAULT_REPETITION_PENALTY", "1"))
MODEL_DEFAULT_LENGTH_PENALTY = float(os.getenv("MODEL_DEFAULT_LENGTH_PENALTY", "1"))

BASE_MODEL_CONFIG = {
    "ENABLE_CUDA": ENABLE_CUDA,
    "LOAD_IN_8BIT": LOAD_IN_8BIT,
    "LOAD_IN_4BIT": LOAD_IN_4BIT,
    "LOW_CPU_MEM_USAGE": LOW_CPU_MEM_USAGE,
    "TARGET_GPU_INDEX": TARGET_GPU_INDEX,
    "MODEL_SEED": MODEL_SEED,
    "MODEL_DEFAULT_NUM_BEAMS": MODEL_DEFAULT_NUM_BEAMS,
    "MODEL_DEFAULT_DO_SAMPLE": MODEL_DEFAULT_DO_SAMPLE,
    "MODEL_DEFAULT_TEMPERATURE": MODEL_DEFAULT_TEMPERATURE,
    "MODEL_DEFAULT_TOP_P": MODEL_DEFAULT_TOP_P,
    "MODEL_DEFAULT_TOP_K": MODEL_DEFAULT_TOP_K,
    "MODEL_DEFAULT_MAX_NEW_TOKENS": MODEL_DEFAULT_MAX_NEW_TOKENS,
    "MODEL_DEFAULT_REPETITION_PENALTY": MODEL_DEFAULT_REPETITION_PENALTY,
    "MODEL_DEFAULT_LENGTH_PENALTY": MODEL_DEFAULT_LENGTH_PENALTY,
}
