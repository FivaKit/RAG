"""Qdrant vector storage and search."""
from qdrant_client import QdrantClient, models

from .config import QDRANT_API_KEY, QDRANT_URL


class VectorDB:
    def __init__(self, client=None):
        self.client = client if client is not None else QdrantClient(
            url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60
        )

    def create_collection(self, collection_name, dim, recreate=False):
        if dim < 1:
            raise ValueError("Размерность векторов должна быть положительной.")
        if self.client.collection_exists(collection_name=collection_name):
            if not recreate:
                raise ValueError(
                    f"Коллекция {collection_name!r} уже существует. "
                    "Для переиндексации используйте --recreate."
                )
            self.client.delete_collection(collection_name=collection_name)
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=dim, distance=models.Distance.COSINE
            ),
        )

    def upload_points(self, vectors, chuncks, collection_name, batch_size=100):
        if len(vectors) != len(chuncks):
            raise ValueError("Количество векторов и чанков не совпадает.")
        if not vectors:
            raise ValueError("Нет векторов для загрузки.")
        if batch_size < 1:
            raise ValueError("batch_size должен быть положительным.")
        dim = len(vectors[0])
        if not dim or any(len(vector) != dim for vector in vectors):
            raise ValueError("Неверная или неодинаковая размерность embeddings.")
        points = (
            models.PointStruct(id=i, vector=vector, payload=chunk)
            for i, (vector, chunk) in enumerate(zip(vectors, chuncks))
        )
        self.client.upload_points(
            collection_name=collection_name,
            points=points, batch_size=batch_size, parallel=1, max_retries=3,
            wait=True,
        )

    def uppload_points(self, vectors, chuncks, collection_name):
        """Backward-compatible alias for the earlier misspelled method."""
        return self.upload_points(vectors, chuncks, collection_name)

    def search_relevant(self, query_vector, top_n, collection_name):
        if top_n < 1:
            raise ValueError("top_n должен быть положительным.")
        if not query_vector:
            raise ValueError("Пустой вектор запроса.")
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector, limit=top_n, with_payload=True,
        ).points
