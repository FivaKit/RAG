import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from main import passage_reference, retrieve_documents
from rag.models.embeddings import Embedder
from rag.reranker import Reranker
from rag.vector_db import VectorDB


class PipelineTests(unittest.TestCase):
    def test_batch_embeddings_preserve_order(self):
        client = MagicMock()
        client.embeddings.create.side_effect = [
            SimpleNamespace(data=[
                SimpleNamespace(index=1, embedding=[2.0]),
                SimpleNamespace(index=0, embedding=[1.0]),
            ]),
            SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[3.0])]),
        ]
        vectors = Embedder(client=client).encode(["a", "b", "c"], batch_size=2)
        self.assertEqual(vectors, [[1.0], [2.0], [3.0]])
        self.assertEqual(client.embeddings.create.call_count, 2)

    def test_reranker_preserves_order(self):
        session = MagicMock()
        session.post.return_value.json.return_value = {
            "results": [{"index": 2}, {"index": 0}]
        }
        ranker = Reranker(api_key="fake", session=session)
        self.assertEqual(ranker.rerank("query", ["a", "b", "c"], 2), ["c", "a"])

    def test_qdrant_upload_and_search(self):
        client = MagicMock()
        client.collection_exists.return_value = False
        db = VectorDB(client=client)
        db.create_collection("test", 2)
        db.upload_points(
            [[1., 0.], [0., 1.]],
            [{"text": "a"}, {"text": "b"}],
            "test",
        )
        points = client.upload_points.call_args.kwargs["points"]
        self.assertEqual([point.payload["text"] for point in points], ["a", "b"])
        client.query_points.return_value.points = ["hit"]
        self.assertEqual(db.search_relevant([1., 0.], 2, "test"), ["hit"])

    def test_retrieval_metadata_after_rerank(self):
        db, embedder, reranker = MagicMock(), MagicMock(), MagicMock()
        embedder.encode.return_value = [[0.1, 0.2]]
        db.search_relevant.return_value = [
            SimpleNamespace(payload={"book": "A", "chapter": 1, "text": "alpha"}),
            SimpleNamespace(payload={"book": "B", "chapter": 2,
                                     "verse_start": "3", "text": "beta"}),
        ]
        reranker.rank.return_value = [1]
        hits = retrieve_documents("q", db, embedder, "bible", 20, 1, reranker)
        self.assertEqual(hits[0]["book"], "B")
        self.assertEqual(passage_reference(hits[0]), "B, глава 2, стих 3")


if __name__ == "__main__":
    unittest.main()
