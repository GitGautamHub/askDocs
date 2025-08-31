### askDOCS System Architecture

#### 1. System Flow Diagram (Textual)

The application follows a simple, three-phase flow: Ingestion, Retrieval, and Generation.

- **Phase 1: Ingestion Pipeline**
  1. **File Upload:** User uploads a document (PDF, DOCX, TXT, or image) via the frontend.
  2. **API Trigger:** The frontend sends the file to the `/api/upload` endpoint.
  3. **Background Task:** FastAPI starts an asynchronous background task.
  4. **Text Extraction:** The file is converted to a PDF if needed. Text is extracted using `pdfplumber` or `python-doctr` (OCR fallback).
  5. **Text Chunking:** The extracted text is split into smaller, manageable chunks.
  6. **Embedding:** Each chunk is converted into a numerical vector (embedding) using the BAAI embedding model.
  7. **Indexing:** The embeddings and their metadata are stored in a FAISS vector index file.
  8. **Status Update:** The ingestion status is updated in the SQLite database throughout the process.

- **Phase 2: Q&A and Retrieval**
  1. **User Query:** User submits a question to the `/api/qa` endpoint.
  2. **Embedding:** The query is converted into an embedding using the same BAAI model.
  3. **Vector Search:** A similarity search is performed on the FAISS index to find the most relevant document chunks.
  4. **Filtering:** For "This document" scope, the search results are filtered by the document's unique `doc_id`.
  5. **Context Generation:** The top-k relevant chunks are used to create a prompt for the LLM.

- **Phase 3: Generation**
  1. **LLM Interaction:** The prompt is sent to the Gemini 1.5 Flash LLM.
  2. **Answer Generation:** The LLM generates a concise, grounded answer based on the provided context.
  3. **Streaming Response:** The answer is sent back to the frontend in real-time as a streaming response.

#### 2. Chunking Choices

- **Chunk Size:** 800 tokens.
- **Chunk Overlap:** 200 tokens.

This configuration was chosen to ensure that each chunk contains sufficient context for the LLM, while the overlap helps prevent important information from being split between two chunks.

#### 3. Metadata Schema

Each chunk is stored in the FAISS index with the following metadata:

```json
{
  "doc_id": "string",       // Unique ID of the original document
  "doc_name": "string",     // Original filename of the document
  "page": "number",         // The page number the chunk was extracted from
  "chunk_id": "number",     // A unique ID for the chunk itself
  "ts": "number"            // A placeholder for timestamp (not actively used in this demo)
}