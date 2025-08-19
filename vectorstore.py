# vectorstore.py
"""
Build FAISS vector index from a recipes CSV.
"""

from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def build_recipe_index(csv_file: str):
    """
    Load recipes from CSV and build a FAISS vector store.

    Args:
        csv_file: path to recipes.csv (expects columns like: name,ingredients,instructions)

    Returns:
        FAISS vector store ready for similarity search.
    """
    loader = CSVLoader(file_path=csv_file, encoding="utf-8")
    documents = loader.load()

    # Keep each row as a single document (large chunk size so we don't split away title/ingredients)
    splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=0)
    chunks = splitter.split_documents(documents)

    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_index = FAISS.from_documents(chunks, embedder)

    return vector_index
