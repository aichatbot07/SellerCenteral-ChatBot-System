import os
import logging
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

# Load .env variables
load_dotenv()

# Define logging level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Set up JSON logger
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)

logger = logging.getLogger("SellerChatbot")
logger.setLevel(LOG_LEVEL)
logger.addHandler(logHandler)
logger.propagate = False  # Avoid duplicate logs if root logger is used

logger.info("Logging configured with JSON format")

# Centralized environment variables
HF_TOKEN = os.environ.get("HF_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# Validate required variables
REQUIRED_ENVS = [
    HF_TOKEN, DEEPSEEK_API_KEY, LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY, GOOGLE_APPLICATION_CREDENTIALS
]

if not all(REQUIRED_ENVS):
    logger.error(" Missing one or more required environment variables.")
    raise ValueError("Missing required environment variables.")

logger.info(" All required environment variables loaded.")
