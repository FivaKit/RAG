
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
JINA_API_KEY = os.environ["JINA_API_KEY"]
