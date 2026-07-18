import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BACKEND_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BACKEND_DIR / "chroma_db"
DOCUMENTS_DIR = Path(__file__).resolve().parent / "data" / "documents"
ORDERS_PATH = Path(__file__).resolve().parent / "data" / "orders.json"
USERS_PATH = Path(__file__).resolve().parent / "data" / "users.json"
COLLECTION_NAME = "nimbusmart_support_kb"

@dataclass(frozen=True)
class Settings:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_model: str
    azure_openai_api_version: str
    azure_openai_embedding_model: str
    cors_origins: tuple[str, ...] = ("http://localhost:5173/",)

@lru_cache()
def get_settings() -> Settings:
    return Settings(
        azure_openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        azure_openai_model=os.environ.get("AZURE_OPENAI_MODEL", ""),
        azure_openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
        azure_openai_embedding_model=os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", ""),
    )