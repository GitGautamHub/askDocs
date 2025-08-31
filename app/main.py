import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import download, qa, status, upload
from app.core.config import settings
from app.services.database import setup_db 
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore", category=UserWarning, module="pdfminer.*")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_db()
    yield

app = FastAPI(
    title="Cloud Document Q&A",
    description="A RAG-based AI assistant for document queries.",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
]

# Add the CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


@app.on_event("startup")
def on_startup():
    setup_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Cloud Document Q&A API"}


app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Include the routers for our endpoints
app.include_router(upload.router, tags=["upload"])
app.include_router(qa.router, tags=["qa"])
app.include_router(download.router, tags=["download"])
app.include_router(status.router, tags=["status"])

# Health Check
@app.get("/api/health", summary="Health Check")
def health_check():
    return {"status": "OK"}
