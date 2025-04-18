import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import logging

# LangChain & vector store imports
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq  # <- LLaMA via Groq
from config.config import logger, GROQ_API_KEY

# ---------- Chatbot Chain Setup ----------

def create_qa_chain(retriever) -> RetrievalQA:
    """
    Creates a RetrievalQA chain where LLaMA provides initial answers and ChatGPT supervises/refines them.
    """
    # Initialize memory for context tracking
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
    logger.info(f"Initialized conversation memory.")

    # Step 1: LLaMA (via Groq) generates the initial response
    llama_llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192", temperature=0.7)
    logger.info("LLaMA initialized.")

    # Step 2: ChatGPT supervises/refines the response
    chatgpt_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
    logger.info("ChatGPT initialized.")

    # Shared prompt
    system_prompt = '''You are a helpful AI assistant for Amazon sellers. 
        Your job is to analyze product reviews and metadata to answer seller queries. 
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

    # Step 1: Run the initial QA with LLaMA
    llama_qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llama_llm,
        retriever=retriever,
        # memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={'prompt': PROMPT}
    )
    llama_qa_chain.memory = memory
    logger.info("LLaMA QA chain ready.")

    # Step 2: Define a wrapper that feeds LLaMA's answer into ChatGPT
    class SupervisorChain:
        def __init__(self, inner_chain, supervisor_llm):
            self.inner_chain = inner_chain
            self.supervisor_llm = supervisor_llm
            # self.memory = inner_chain.memory  # reuse memory

        def invoke(self, inputs):
            llama_response = self.inner_chain.invoke(inputs)

            # Extract context (relevant documents)
            source_text = "\n\n".join([doc.page_content for doc in llama_response.get("source_documents", [])])

            # Supervisor (ChatGPT) receives both the context and the LLaMA's draft response
            prompt = f"""You are a supervisor AI that improves answers generated by another assistant.

            Your task is to read the assistant's draft answer below and improve it based on the relevant context. Do NOT include any headings or labels like "Question" or "Improved Answer" — just return the clean, final version of the answer. 
            Remember you are speaking with a seller and don't tell him what to do with the reviews. Only tell him what he can do to improve the product if required and don't do it if it's not necessary and the reviews are positive

            Here's the question that was asked to the assistant:
            {inputs}

            Relevant Context:
            {source_text}

            Assistant's Draft Answer:
            {llama_response['answer']}
            """
            improved_response = self.supervisor_llm.invoke(prompt).content
            return {"answer": improved_response, "source_documents": llama_response.get("source_documents", [])}

        @property
        def memory(self):
            return self.inner_chain.memory

    qa_chain = SupervisorChain(llama_qa_chain, chatgpt_llm)
    logger.info("Supervisor QA chain ready.")
    return qa_chain
