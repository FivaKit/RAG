"""Entry point for indexing and querying the Russian Bible RAG."""
import argparse
from pathlib import Path

import pandas as pd

from rag.chuncker import Chuncker
from rag.models.LLM import Model
from rag.models.embeddings import Embedder
from rag.reranker import Reranker
from rag.vector_db import VectorDB

DATA_PATH = Path(__file__).resolve().parent / "data.csv"


def positive_int(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Введите целое число.") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("Ожидается положительное целое число.")
    return number


def build_parser():
    parser = argparse.ArgumentParser(description="RAG по Синодальному переводу Библии.")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Проиндексировать стихи в Qdrant.")
    index.add_argument("--data", type=Path, default=DATA_PATH)
    index.add_argument("--collection", default="bible")
    index.add_argument("--max-tokens", type=positive_int, default=250)
    index.add_argument("--batch-size", type=positive_int, default=16)
    index.add_argument("--recreate", action="store_true")

    for name in ("ask", "chat"):
        cmd = commands.add_parser(name, help="Задать вопрос" if name == "ask" else "Диалог")
        if name == "ask":
            cmd.add_argument("query")
        cmd.add_argument("--collection", default="bible")
        cmd.add_argument("--top-k", type=positive_int, default=20)
        cmd.add_argument("--top-n", type=positive_int, default=5)
        cmd.add_argument("--no-rerank", action="store_true")
    return parser


def index_documents(args):
    data = pd.read_csv(args.data)
    missing = {"book", "chapter", "text"} - set(data.columns)
    if missing:
        raise ValueError("Отсутствуют столбцы CSV: " + ", ".join(sorted(missing)))
    data = data.dropna(subset=["book", "chapter", "text"])
    chunks = Chuncker().get_chuncks(data, max_length=args.max_tokens)
    if not chunks:
        raise ValueError("Нет непустых чанков для индексации.")
    print(f"Чанков: {len(chunks)}", flush=True)
    vectors = Embedder().encode(
        [chunk["text"] for chunk in chunks], batch_size=args.batch_size
    )
    db = VectorDB()
    db.create_collection(
        args.collection, dim=len(vectors[0]), recreate=args.recreate
    )
    db.upload_points(vectors, chunks, args.collection)
    print(f"Готово: {len(chunks)} чанков в коллекции {args.collection!r}.")


def passage_reference(chunk):
    book, chapter = chunk.get("book", "?"), chunk.get("chapter", "?")
    start, end = chunk.get("verse_start"), chunk.get("verse_end")
    if start is None:
        return f"{book}, глава {chapter}"
    if end is not None and str(start) != str(end):
        return f"{book}, глава {chapter}, стихи {start}–{end}"
    return f"{book}, глава {chapter}, стих {start}"


def retrieve_documents(query, db, embedder, collection, top_k, top_n, reranker):
    query_vector = embedder.encode(query)[0]
    hits = db.search_relevant(query_vector, top_k, collection)
    chunks = [
        dict(hit.payload)
        for hit in hits
        if hit.payload and isinstance(hit.payload.get("text"), str)
        and hit.payload["text"].strip()
    ]
    if reranker is None:
        return chunks[:top_n]
    if not chunks:
        return []
    indices = reranker.rank(
        query, [chunk["text"] for chunk in chunks], min(top_n, len(chunks))
    )
    return [chunks[i] for i in indices]


class RAGApplication:
    def __init__(self, args):
        self.collection, self.top_k, self.top_n = (
            args.collection, args.top_k, args.top_n
        )
        self.db = VectorDB()
        self.embedder = Embedder()
        self.reranker = None if args.no_rerank else Reranker()
        self.llm = Model()

    def ask(self, query):
        chunks = retrieve_documents(
            query, self.db, self.embedder, self.collection,
            self.top_k, self.top_n, self.reranker,
        )
        if not chunks:
            return "Не найдено релевантных отрывков.", []
        passages = [
            f"[{i}] {passage_reference(chunk)}\n{chunk['text']}"
            for i, chunk in enumerate(chunks, start=1)
        ]
        return self.llm.answer(query, passages), chunks


def print_answer(answer, chunks):
    print("\n" + answer)
    if chunks:
        print("\nИспользованные отрывки:")
        for i, chunk in enumerate(chunks, start=1):
            print(f"  [{i}] {passage_reference(chunk)}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "index":
        index_documents(args)
        return
    application = RAGApplication(args)
    if args.command == "ask":
        print_answer(*application.ask(args.query))
        return
    print("Интерактивный RAG. Для выхода введите exit.")
    while True:
        try:
            query = input("\nВопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ("exit", "quit", "выход"):
            break
        if query:
            print_answer(*application.ask(query))


if __name__ == "__main__":
    main()
