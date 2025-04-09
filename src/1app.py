import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
from langchain.prompts import PromptTemplate
from Data.meta_data import fetch_metadata
from Data.fetch_reviews import fetch_reviews
from chain import create_qa_chain 
from retriever import create_retriever_from_df 
from model_evaluation.bias_detection import detect_bias, analyze_sentiments
from model_evaluation.tracking_code import log_chat_interaction
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
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not all([HF_TOKEN, DEEPSEEK_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, GOOGLE_APPLICATION_CREDENTIALS]):
    raise ValueError("One or more required environment variables are missing.")
# Set up BigQuery credentials; ensure GOOGLE_APPLICATION_CREDENTIALS points to your file
# For example, if using a file mounted in your container:


# ---------- Streamlit Interface ----------

# Set up the Streamlit page

st.set_page_config(page_title="Amazon Seller Central Chatbot", page_icon="🤖", layout="wide")
st.title("Amazon Seller Central Chatbot")
st.subheader("Your Intelligent Seller Companion")

# Input: Product ASIN
asin = st.text_input("Enter your product ASIN:", key="asin_input")

if asin:
    st.info("Fetching data from BigQuery...")
    review_df = fetch_reviews(asin)
    meta_df = fetch_metadata(asin)
    
    if review_df.empty:
        st.error("No review data found for the provided ASIN.")
    else:
        st.success("Data fetched successfully!")
        st.write("Sample Review Data:", review_df.head())
        st.write("Sample Metadata:", meta_df.head())

        

        # Create a retriever from the reviews DataFrame
        retriever = create_retriever_from_df(review_df)
        # Create the QA chain using the retriever
        qa_chain = create_qa_chain(retriever)

        # Input: User question
        user_question = st.text_input("Ask a question about your product:", key="user_question")
        
        if user_question:
            st.info("Generating answer...")
            try:
                # Run the chain to generate an answer
                answer = qa_chain.invoke(user_question)
                st.markdown("**Answer:**")
                st.write(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")
                
            # Call bias detection
            review_sentiments = analyze_sentiments(review_df)
            bias_result = detect_bias(answer, review_sentiments, len(review_df))
            if bias_result["bias_detected"]:
                st.warning(f"Bias detected: {bias_result['bias_types']}")
            else:
                st.success("No bias detected.")
            
            log_chat_interaction(user_question, answer,model_name="deepseek-chat", temperature=0.5)
        
        # Display conversation history
        st.markdown("### Conversation History")
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
            st.write(f"**{role}:** {content}")
