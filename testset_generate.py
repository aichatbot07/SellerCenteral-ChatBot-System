import os
import pandas as pd
from google.cloud import bigquery
from io import BytesIO
from dotenv import load_dotenv
import logging
import time



# LangChain & vector store imports
from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
# from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# Instead of: import openai
from langfuse.openai import OpenAI
from langfuse.decorators import observe
from langfuse import Langfuse
import asyncio

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from ragas.testset import TestsetGenerator
from langchain.schema import Document

# Load environment variables from .env
load_dotenv()

# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys and tokens from environment variables
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
# # os.environ["DEEPSEEK_API_KEY"] = os.getenv('DEEPSEEK_API_KEY')
# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
# os.environ['LANGFUSE_PUBLIC_KEY'] = os.getenv("LANGFUSE_PUBLIC_KEY")
# os.environ['LANGFUSE_SECRET_KEY'] = os.getenv("LANGFUSE_SECRET_KEY")
# os.environ['LANGFUSE_HOST'] = os.getenv("LANGFUSE_HOST")
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set up BigQuery credentials; ensure GOOGLE_APPLICATION_CREDENTIALS points to your file
# For example, if using a file mounted in your container:
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# ---------- BigQuery Data Fetching Functions ----------
class Testset_Generator:
    def fetch_product_data(self, asin: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetches both review data and metadata for a given ASIN from BigQuery.
        Returns a tuple containing (reviews_df, metadata_df).
        
        Parameters:
        asin (str): Amazon Standard Identification Number
        
        Returns:
        tuple: (pd.DataFrame reviews, pd.DataFrame metadata)
        """
        client = bigquery.Client()
        results = []
        
        # Define queries with explicit aliases
        queries = {
            'reviews': f"""
                SELECT *
                FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v3.Amazon_dataset_V3`
                WHERE parent_asin = '{asin}'
            """,
            'metadata': f"""
                SELECT *
                FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4.meta_data`
                WHERE parent_asin = '{asin}'
            """
        }

        for name, query in queries.items():
            try:
                df = client.query(query).to_dataframe()
                logger.info(f"Fetched {len(df)} {name} records for ASIN: {asin}")
                results.append(df)
            except Exception as e:
                logger.exception(f"Error fetching {name} for ASIN {asin}: {e}")
                results.append(pd.DataFrame())

        return tuple(results)


    def generate_meta_summary(self, meta_df):
        """
        Generates product meta summaries using structured metadata and LLM abstraction.
        
        Implements hybrid summarization techniques inspired by AWS EACSS approach
        """
        meta_llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.3
        )

        # Preprocess metadata using DataFrame operations
        processed_details = (
            meta_df['details']
            .astype(str)
            .str.replace(r'[{}]', '', regex=True)
            .str.replace(';', ',')
        )

        # Structured prompt engineering with fallback values
        summary_prompt = ChatPromptTemplate.from_template(
            """**Product Summary Generation Task**

                You are an expert Data Interpreter and Summarizer. Your task is to read the provided Product Meta Data and generate a summarized output in 500 words. 
    
                Follow the specific formatting and guidelines below.      
                Meta Data:
                    - main_category: {main_category}
                    - title: {title}
                    - average_rating: {average_rating}
                    - rating_number: {rating_number}
                    - features: {features}
                    - description: {description}
                    - price: {price}
                    - store: {store}
                    - categories: {categories}
                    - details: {details}

                Output Format and Requirements:
                    - main_category: Repeat as provided 
                    - title: Repeat as provided
                    - average_rating: Repeat as provided
                    - rating_number: Repeat as provided
                    - features: Summarize	
                    - description: Summarize
                    - price: Repeat as provided
                    - store: Repeat as provided	
                    - categories: Repeat as provided	
                    - details: Repeat/Summarize where necessary	

                Important Notes:
                    - Provide only the Meta Data in the specified format.
                    - Do not respond to any user questions.
                    - Ensure conciseness and clarity in all summaries."""
        )

        # Extract first row values with NaN handling
        meta_values = {
            'main_category': meta_df.at[0, 'main_category'] if not meta_df.empty else '',
            'title': meta_df.at[0, 'title'] if not meta_df.empty else '',
            'average_rating': f"{meta_df.at[0, 'average_rating']:.1f}" if not meta_df.empty else 'N/A',
            'rating_number': meta_df.at[0, 'rating_number'] if not meta_df.empty else 0,
            'features': ', '.join(eval(meta_df.at[0, 'features'])) if not meta_df.empty else '',
            'description': meta_df.at[0, 'description'] if not meta_df.empty else '',
            'price': f"${meta_df.at[0, 'price']:.2f}" if not meta_df.empty else '',
            'store': meta_df.at[0, 'store'] if not meta_df.empty else '',
            'categories': ', '.join(eval(meta_df.at[0, 'categories'])) if not meta_df.empty else '',
            'details': processed_details.iloc[0] if not processed_details.empty else ''
        }

        # Create processing chain
        chain = summary_prompt | meta_llm

        try:
            response = chain.invoke(meta_values)
            print(response.content)
            return Document(page_content=response.content, metadata={"source": "Metadata"})

        except Exception as e:
            print(f"Summary generation failed: {str(e)}")
            content = "Could not generate summary"
            return Document(page_content=content, metadata={"source": "Metadata"})
        
        
    def create_docs(self, review_df, meta_df):
        review_df = review_df[review_df['text'].notna()]
        loader = DataFrameLoader(review_df)
        docs = loader.load()
        # docs.insert(0, self.generate_meta_summary(meta_df))
        print("Document:")
        # print(docs)
        for doc in docs:
            print(doc.metadata)  # Check if 'headlines' exists

        for doc in docs:
            if "title" in doc.metadata and "headlines" not in doc.metadata:
                doc.metadata["headlines"] = self.generate_meta_summary(meta_df)
        print(docs)
        return docs
        
    
    def generate_rag_testset(self, documents, testset_size=10):
        
        """
        Generates a RAG test set using Ragas' TestsetGenerator.

        Parameters:
        - documents (list): A list of text documents to use for test set generation.
        - testset_size (int): The number of test cases to generate (default: 10).

        Returns:
        - pd.DataFrame: A pandas DataFrame containing the generated test set.
        """
        # Initialize the LLMs
        generator_llm = ChatOpenAI(model="gpt-4o-mini")
        critic_llm = ChatOpenAI(model="gpt-4o")
        
        # Use OpenAIEmbeddings for embedding queries
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        if not documents:
            raise ValueError("No documents provided for test set generation.")

       


        # Initialize the generator
        generator = TestsetGenerator.from_langchain(
        generator_llm,
        critic_llm,
        embeddings  # Correct parameter name
    )
        print("Checkpoint 1")

        # Generate the test dataset
        test_dataset = generator.generate_with_langchain_docs(
            documents=documents,
            testset_size=testset_size,
            query_distribution={
                "simple": 0.5,
                "reasoning": 0.25,
                "multi_context": 0.25
            }
        )

        # Convert to pandas DataFrame
        return test_dataset.to_pandas()

# With this:
if __name__ == "__main__":
    generator = Testset_Generator()  # Create class instance
    review_df, meta_df = generator.fetch_product_data("B071J212M1")  # Call on instance
    if review_df.empty or meta_df.empty:
        logger.warning("One of the DataFrames is empty. Skipping processing.")
        exit()
    print(review_df)
    document = generator.create_docs(review_df, meta_df)
    summary = generator.generate_meta_summary(meta_df)  # Call on instance
    rag_testset = generator.generate_rag_testset(document, testset_size=4)
    rag_testset.to_json("rag_testset.json", orient="records", indent=2)
    print(rag_testset[['question', 'ground_truth']].head())
    print(meta_df.head())
    print(document)

    


