import os
import pandas as pd
import logging
# LangChain & vector store imports
from langchain.chains import RetrievalQA

from langchain.memory import ConversationBufferMemory
from langchain_deepseek import ChatDeepSeek

from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys and tokens from environment variables
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
# os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ["DEEPSEEK_API_KEY"] = os.getenv('DEEPSEEK_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['LANGFUSE_PUBLIC_KEY'] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ['LANGFUSE_SECRET_KEY'] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ['LANGFUSE_HOST'] = os.getenv("LANGFUSE_HOST")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set up BigQuery credentials; ensure GOOGLE_APPLICATION_CREDENTIALS points to your file
# For example, if using a file mounted in your container:
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# ---------- Chatbot Chain Setup ----------

def create_qa_chain(retriever) -> RetrievalQA:
    """
    Creates a RetrievalQA chain using an LLM and conversation memory.
    """
    # Initialize conversation memory to track chat history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,output_key="answer")
    # Initialize the chat LLM (e.g., GPT-4)
    llm = ChatDeepSeek(model_name="deepseek-chat", temperature=0.5)
    system_prompt = """You are a highly intelligent assistant for Amazon eCommerce sellers. 
                            Analyze the provided product data and answer seller-related queries. 
                            Just answer concisely.

                            Relevant Data:
                            {context}

                            Question: {question}
                            """
    PROMPT = PromptTemplate(template=system_prompt, input_variables=["context", "question"])
    # Build a RetrievalQA chain using a simple "stuff" chain type
    qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory, return_source_documents=True,
        combine_docs_chain_kwargs={'prompt': PROMPT})
    # qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, memory=memory, combine_docs_chain_kwargs={"prompt": PROMPT})
    return qa_chain