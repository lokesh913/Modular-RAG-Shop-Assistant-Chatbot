import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# Lazy-initialized singleton to avoid crashing on import
_vectorstore = None


def get_vectorstore():
    """Return a cached PineconeVectorStore instance, creating it on first call."""
    global _vectorstore
    if _vectorstore is None:
        # Init embedding model
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=768)

        # Init Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("shop-product-catalog")

        # Init vectorstore
        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=embedding_model,
            text_key="Description"
        )
    return _vectorstore