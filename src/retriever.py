import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import logging
# LangChain & vector store imports
from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import logging
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS

# ---------- Retriever Creation ----------

def create_retriever_from_df(review_df: pd.DataFrame):
    """
    Converts the review DataFrame into a vector database retriever using FAISS.
    """
    try:
        # Use DataFrameLoader to convert the DataFrame into documents
        review_df['combined_text'] = review_df.astype(str).apply(lambda row: ' | '.join(row.values), axis=1)
        loader = DataFrameLoader(review_df, page_content_column="combined_text")
        review_docs = loader.load()
        logger.info(f"Loaded {len(review_docs)} review documents.")
        logger.info(f"Review Documents: {review_docs}")
        review_docs = [doc for doc in review_docs if isinstance(doc.page_content, str)]
    except Exception as e:
        logger.exception("Error loading documents from DataFrame: " + str(e))
        review_docs = []
    
    # Create embeddings using a HuggingFace model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # Build the vector store using FAISS
    vectordb = FAISS.from_documents(documents=review_docs, embedding=embeddings)
    retriever = vectordb.as_retriever()
    return retriever
