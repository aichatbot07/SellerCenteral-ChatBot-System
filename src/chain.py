import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import logging
# LangChain & vector store imports
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_deepseek import ChatDeepSeek
from accelerate import init_empty_weights
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
# Set up logging (optional; adjust format as needed)
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS


# ---------- Chatbot Chain Setup ----------

def create_qa_chain(retriever) -> RetrievalQA:
    """
    Creates a RetrievalQA chain using an LLM and conversation memory.
    """
    # Initialize conversation memory to track chat history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,output_key="answer")
    logger.info(f"Done memory process!!!")
    # Initialize the chat LLM (e.g., GPT-4)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
    logger.info(f"Done llm process!!!")
    system_prompt = '''You are a helpful AI assistant for Amazon sellers. 
                            Your job is to analyze product reviews and metadata to answer seller queries.. 
                            Your responses should be clear, concise, and insightful.

                            Relevant Data:
                            {context}

                            Question: {question}
                            Guidelines:
                            - Summarize insights from reviews if applicable.
                            - Avoid including raw review text unless explicitly requested.
                            - Format your response in a readable way.
                            '''
    PROMPT = PromptTemplate(template=system_prompt, input_variables=["context", "question"])
    # Build a RetrievalQA chain using a simple "stuff" chain type
    qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory, return_source_documents=True,
        combine_docs_chain_kwargs={'prompt': PROMPT})
    logger.info(f"Done qa_chain process!!!")
    # qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, memory=memory, combine_docs_chain_kwargs={"prompt": PROMPT})
    return qa_chain