import os
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.core.config import settings
from app.core.utils import log_timing
from app.services.vector_db import load_faiss_index, merge_faiss_indexes
from dotenv import load_dotenv
load_dotenv()
router = APIRouter()

class QA_Request(BaseModel):
    query: str
    scope: str 
    doc_id: Optional[str] = None 

@router.post("/api/qa", summary="Answer a question based on documents")
@log_timing
async def answer_question(request: QA_Request):
    index_dir = settings.FAISS_INDEX_DIR
    if request.scope == "this_document":
        if not request.doc_id:
            return {"answer": "Please specify a document ID for 'this_document' scope."}
        vector_store = load_faiss_index(index_dir, request.doc_id)
        if not vector_store:
            return {
                "answer": "I don't have information on that document. Please try again."
            }
    elif request.scope == "all_documents":
        vector_store = merge_faiss_indexes(index_dir)
        if not vector_store:
            return {
                "answer": "I don't have any documents to answer this question from."
            }
    else:
        return {"answer": "Invalid scope provided."}

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10}
    )  # Top-k retrieval 10

    retrieved_docs = retriever.invoke(request.query)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash"
    )
    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an expert AI assistant that provides answers based solely on the provided documents.
        Answer the following question using ONLY the context provided below.
        If the context does not contain enough information to answer the question, state that you cannot find the answer in the documents.
        Do not make up any information.
        
        Context:
        {context}
        
        Question: {question}

        Provide a concise answer. Always give top 3 citations using the format [Source: doc_name, Page: page_number].
        """
    )

    context = "\n".join(
        [
            f"Document: {doc.metadata['doc_name']}, Page: {doc.metadata['page']}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    final_prompt = prompt_template.format(context=context, question=request.query)
    # Stream the response 
    async def stream_generator():
        for chunk in llm.stream(final_prompt):
            yield chunk.content
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")