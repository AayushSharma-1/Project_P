# Import necessary libraries
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
from FinalApplicationFiles.embeddings.embeddings import initialize_embeddings 
from FinalApplicationFiles.VectorDB.pinecone_setup import PineconeVectorDatabase
from FinalApplicationFiles.LLMs.llm import initialize_llm, create_rag_chain
# Load environment variables from .env file

load_dotenv()

# Fetch API keys from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")  # Pinecone API key
gemini_api_key = os.getenv("GEMINI_API_KEY")



# PVC.setup_pinecone, PVC.retrieve_documents  # Google Generative AI key

def main():

    # Initialize embeddings model
    embeddings = initialize_embeddings()

    # Setup Pinecone connection and index
    index_name = "pib"
    PVC = PineconeVectorDatabase(pinecone_api_key, index_name, embeddings)
    vector_store = PVC._setup_pinecone()

    # Retrieve documents from the vector store (no vector addition)
    retriever = PVC.retrieve_documents()

    # Initialize the Google Generative AI model
    llm = initialize_llm(gemini_api_key)
    print(retriever.invoke("Tell me about Swachh Bharat Mission"))

    # Create the RAG chain (Retrieval-Augmented Generation)
    rag_chain = create_rag_chain(retriever, llm)

    # Loop to ask multiple questions
    while True:
        question = input("Enter your question (or type 'exit' to stop): ")

        if question.lower() == 'exit':
            print("Exiting the Q&A session.")
            break
        
        # Use the chain to generate an answer
        ans = rag_chain.invoke(question)
    

        # Print the generated answer
        print(f"Answer: {ans}")

        print("\n")  # Blank line between questions

if __name__ == "__main__":
    main()