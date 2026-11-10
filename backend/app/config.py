import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
DEFAULT_KB_DIR = ROOT_DIR / "knowledge_base"

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareFlow NLP"
    PROJECT_DESCRIPTION: str = "Healthcare Query Understanding & Intelligent Response System"
    VERSION: str = "1.0.0"
    
    # LLM Settings
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    
    # Embedding & Retrieval Settings
    EMBEDDING_MODEL_NAME: str = "tfidf"  # Uses lightweight TF-IDF (no model downloads)
    EMBEDDING_DIMENSION: int = 384
    TOP_K_RETRIEVAL: int = 3
    SIMILARITY_THRESHOLD: float = 0.25
    KNOWLEDGE_BASE_DIR: str = str(DEFAULT_KB_DIR)
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

