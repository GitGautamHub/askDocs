# app/services/vector_db.py
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def get_faiss_embeddings():
    """Returns the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# function to create and save FAISS index
def create_and_save_faiss_index(text_content: str, doc_name: str, doc_id: str, index_dir: str):
    embeddings = get_faiss_embeddings()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )
    docs = text_splitter.create_documents([text_content])
    file_extension = os.path.splitext(doc_name)[1].lower()
    is_single_page = file_extension in [".jpg", ".jpeg", ".png", ".txt", ".pdf"]

    for i, doc in enumerate(docs):
        # logic for determining page number
        page_number = 1 if is_single_page else i + 1
        
        doc.metadata = {
            "doc_id": doc_id,
            "doc_name": doc_name,
            "page": page_number,
            "chunk_id": i,
            "ts": 0
        }

    vector_store = FAISS.from_documents(docs, embeddings)
    
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    vector_store.save_local(index_dir, index_name=doc_id)

    return True

# function to load FAISS index
def load_faiss_index(index_dir: str, index_name: str):
    embeddings = get_faiss_embeddings()
    try:
        return FAISS.load_local(
            index_dir,
            embeddings,
            index_name=index_name,
            allow_dangerous_deserialization=True,
        )
    except RuntimeError as e:
        print(f"Error loading FAISS index: {e}")
        return None

# function to merge FAISS indexes
def merge_faiss_indexes(index_dir: str):
    embeddings = get_faiss_embeddings()
    index_files = [f for f in os.listdir(index_dir) if f.endswith(".faiss")]

    if not index_files:
        return None

    first_index_name = os.path.splitext(index_files[0])[0]
    merged_index = load_faiss_index(index_dir, first_index_name)

    for i in range(1, len(index_files)):
        index_name = os.path.splitext(index_files[i])[0]
        current_index = load_faiss_index(index_dir, index_name)
        if current_index:
            merged_index.merge_from(current_index)

    return merged_index
