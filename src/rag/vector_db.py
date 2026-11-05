from qdrant_client import QdrantClient, models
from transformers import Chunk

class VectorDB:

    def __init__(self):
        self.client = QdrantClient(url="http://localhost:6333")

    def create_collection(self, collection_name, dim=1024):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=dim,
                distance=models.Distance.COSINE
            )
        )

    def uppload_points(self, vectors, chuncks, collection_name):

        self.points = (models.PointStruct(
            id=i,
            vector=vector,
            payload=chunck
            )
            for i, (chunck, vector) in enumerate(zip(chuncks, vectors))
        )

        self.client.upload_points(
            collection_name=collection_name,
            points = self.points,
            batch_size=100,
            parallel=1,
            max_retries=3
        )

    def search_relevant(self, query_vector, top_n, collection_name):

        results = self.client.query_points(
            collection_name=collection_name,
            query = query_vector,
            limit = top_n,
            with_payload=True
        ).points

        return results


