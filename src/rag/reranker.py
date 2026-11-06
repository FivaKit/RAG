"""Jina Reranker API adapter."""
import requests

from .config import JINA_API_KEY, require_key


class Reranker:
    def __init__(self, api_key=None, model="jina-reranker-v3.5", session=None):
        self.url = "https://api.jina.ai/v1/rerank"
        self.api_key = require_key(
            "JINA_API_KEY", JINA_API_KEY if api_key is None else api_key
        )
        self.model = model
        self.session = session if session is not None else requests

    def rank(self, query, documents, top_n):
        if not documents:
            return []
        if top_n < 1:
            raise ValueError("top_n должен быть положительным.")
        response = self.session.post(
            self.url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={
                "model": self.model, "query": query,
                "top_n": min(top_n, len(documents)),
                "documents": documents, "return_documents": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        results = response.json()["results"]
        indices = [int(item["index"]) for item in results]
        if any(i < 0 or i >= len(documents) for i in indices):
            raise ValueError("Jina вернула некорректный индекс документа.")
        return indices

    def rerank(self, query, documents, top_n):
        return [documents[i] for i in self.rank(query, documents, top_n)]
