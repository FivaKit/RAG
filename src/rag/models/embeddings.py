"""Batched embeddings via OpenRouter."""
from openai import OpenAI

from ..config import EMBEDDING_MODEL, OPENROUTER_API_KEY, require_key


class Embedder:
    def __init__(self, model=EMBEDDING_MODEL, client=None):
        self.model = model
        self.client = client if client is not None else OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=require_key("OPENROUTER_API_KEY", OPENROUTER_API_KEY),
            timeout=180,
            max_retries=3,
        )

    def encode(self, input, batch_size=16):
        if batch_size < 1:
            raise ValueError("batch_size должен быть положительным.")
        texts = [input] if isinstance(input, str) else list(input)
        if not texts:
            return []
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Тексты для embeddings должны быть непустыми строками.")
        vectors = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            result = self.client.embeddings.create(
                model=self.model, input=batch, encoding_format="float"
            )
            ordered = sorted(result.data, key=lambda item: item.index)
            if len(ordered) != len(batch):
                raise RuntimeError("API вернул меньше embeddings, чем было текстов.")
            if [item.index for item in ordered] != list(range(len(batch))):
                raise RuntimeError("API вернул некорректные индексы embeddings.")
            vectors.extend(item.embedding for item in ordered)
        return vectors
