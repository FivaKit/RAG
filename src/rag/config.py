"""Shared application configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
EMBEDDING_MODEL = os.getenv(
    "OPENROUTER_EMBEDDING_MODEL", "liquid/lfm-2.5-embedding-350m:free"
)
CHAT_MODEL = os.getenv(
    "OPENROUTER_CHAT_MODEL", "nvidia/nemotron-3.5-super-vl:free"
)
TOKENIZER_MODEL = os.getenv(
    "TOKENIZER_MODEL", "nvidia/Nemotron-3.5-Embed-1B-BF16"
)


def require_key(name, value):
    if not value:
        raise ValueError(
            f"Не задан {name}. Скопируйте src/.env.example в src/.env "
            "и укажите API-ключ."
        )
    return value
