# RAG Document QA (MVP)

Overview:
- RAG system to upload documents and query them via vector similarity + LLM.
- FastAPI backend, FAISS vector store, sentence-transformers embeddings.

## Features

- Upload PDF, TXT, DOCX documents  
- Automatic text chunking and embedding  
- Vector similarity search with FAISS  
- Beautiful React frontend  
- RESTful API with Swagger docs  
- Caching for embeddings  

## Tech Stack

- **Backend:** FastAPI, FAISS, Sentence-Transformers, LangChain
- **Frontend:** React 18, Vite
- **Vector Store:** FAISS (CPU)
- **Embeddings:** all-MiniLM-L6-v2
- **Document Parsing:** PyPDF2, python-docx

## Installation

### Quick Setup (Recommended)

Linux/macOS:

```bash
chmod +x scripts/setup-full.sh
./scripts/setup-full.sh
```

Windows PowerShell:

```powershell
.\scripts\setup-full.ps1
```

### Manual Setup

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Install and build frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

4. Create `.env` file:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional for basic RAG)
```

## Usage

### Start the Application

```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Run FastAPI server
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Open browser: [http://localhost:8000](http://localhost:8000)

### API Endpoints

- `GET /` — Root endpoint with API info
- `GET /health` — Health check
- `POST /upload` — Upload document (PDF, TXT, DOCX)
- `POST /query` — Query documents
- `GET /documents` — List uploaded documents
- `DELETE /documents/{id}` — Remove document
- `GET /docs` — Swagger UI documentation

### Example Usage

Upload a document:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@path/to/document.pdf"
```

Query documents:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the main topic?","top_k":5}'
```

## Architecture

```
???????????????????????????????????????????
?         React Frontend (SPA)             ?
?      Upload | Query Results Display      ?
???????????????????????????????????????????
               ? HTTP API
???????????????????????????????????????????
?         FastAPI Backend                  ?
?  /upload  /query  /documents  /health   ?
????????????????????????????????????????????
           ?                       ?
    ??????????????        ????????????????
    ? Embeddings ?        ? Document     ?
    ? Manager    ?        ? Loader       ?
    ? (Cache)    ?        ? (PDF/TXT...)?
    ??????????????        ????????????????
           ?                      ?
    ??????????????????????????????????
    ?      Vector Store (FAISS)       ?
    ?  - Similarity Search            ?
    ?  - Metadata Filtering           ?
    ?  - Persistence (disk)           ?
    ???????????????????????????????????
```

## Development

### Frontend Development

```bash
cd frontend
npm run dev  # Start Vite dev server on localhost:5173
```

### Backend Development

```bash
uvicorn src.api:app --reload --log-level debug
```

## Project Structure

```
rag-document-qa/
--- frontend/                 # React frontend
-   --- src/
-   -   --- App.jsx
-   -   --- App.css
-   -   --- components/
-   -   -   --- Upload.jsx
-   -   -   --- Upload.css
-   -   -   --- Query.jsx
-   -   -   --- Query.css
-   -   --- main.jsx
-   --- index.html
-   --- package.json
-   --- vite.config.js
-   --- dist/               # Built frontend (after npm run build)
--- src/
?   ??? api.py              # FastAPI application
?   ??? document_loader.py  # PDF/TXT/DOCX loader
?   ??? embeddings.py       # Embedding manager
?   ??? vector_store.py     # FAISS wrapper
?   ??? rag_chain.py        # RAG pipeline (LangChain)
??? utils/
?   ??? preprocessing.py    # Text chunking & cleaning
??? scripts/
?   ??? setup-full.sh       # Full setup (bash)
?   ??? setup-full.ps1      # Full setup (PowerShell)
??? requirements.txt        # Python dependencies
??? .env.example           # Example environment variables
??? README.md              # This file
```

## Performance Metrics

- **Embedding Speed:** ~1000 tokens/sec (all-MiniLM-L6-v2)
- **FAISS Search:** <100ms for top-5 results
- **Memory:** ~500MB for 10K documents

## Future Improvements

- [ ] LLM-based answer generation (OpenAI GPT-3.5/4)
- [ ] Conversation memory for follow-up questions
- [ ] Multi-language support
- [ ] Advanced filtering and metadata search
- [ ] Document preview in UI
- [ ] Batch document upload
- [ ] Export results as PDF

## Troubleshooting

**Issue:** "No documents indexed yet"
- Solution: Upload a document first via the Upload form

**Issue:** Embedding cache errors
- Solution: Delete `embeddings_cache.pkl` and `faiss*.pkl` files; re-upload documents

**Issue:** Frontend not loading
- Solution: Run `cd frontend && npm run build` then restart the server

## License

MIT

## Support

For issues or questions, open a GitHub issue or check the API docs at `/docs`
