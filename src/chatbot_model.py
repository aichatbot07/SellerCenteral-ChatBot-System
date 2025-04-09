import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import logging

# LangChain & vector store imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from Data.fetch_reviews import fetch_reviews
from Data.meta_data import fetch_metadata
from accelerate import init_empty_weights
from src.chain import create_qa_chain 
from src.retriever import create_retriever_from_df 

# Load environment variables from .env
load_dotenv()

# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys and tokens from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY= os.getenv('DEEPSEEK_API_KEY')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
import json

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Write the secret to a file to be used by the GCP client libraries
if GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_APPLICATION_CREDENTIALS.startswith("{"):
    with open("/app/service_account.json", "w") as f:
        f.write(GOOGLE_APPLICATION_CREDENTIALS)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/service_account.json"


if not all([HF_TOKEN, DEEPSEEK_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, GOOGLE_APPLICATION_CREDENTIALS]):
    raise ValueError("One or more required environment variables are missing.")

def chatbot(asin, user_question):
    try:
        logger.info(f"Processing ASIN: {asin}")
        # Fetch reviews and metadata
        review_df = fetch_reviews(asin)
        meta_df = fetch_metadata(asin)

        if review_df.empty:
            logger.warning(f"No reviews found for ASIN: {asin}")
            return "No review data found for the provided ASIN.", []

        # Create a retriever from the reviews DataFrame
        retriever = create_retriever_from_df(review_df)

        # Create the QA chain using the retriever
        qa_chain = create_qa_chain(retriever)
        logger.info(f"Done retriever process!!!")

        # Generate an answer using the QA chain
        answer = qa_chain.invoke({'question': user_question})
        logger.info(f"Generated response: {answer['answer']}")
        # Extract conversation history
        conversation_history = qa_chain.memory.chat_memory.messages
        for msg in qa_chain.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                role = "User"
            elif isinstance(msg, AIMessage):
                role = "Assistant"
            elif isinstance(msg, SystemMessage):
                role = "System"
            else:
                role = "Unknown"
            content = msg.content

        return answer['answer'] 

    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return f"Error processing query: {str(e)}", []
