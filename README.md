# RAG по русской Библии

Учебный RAG без LangChain/LlamaIndex: тексты из `src/data.csv`, чанкинг по
главам, embedding через OpenRouter, Qdrant, Jina Reranker и LLM.
`src/rag/parser.py` — старый парсер УК РФ, в текущем RAG он не используется.

## Установка

Из корня репозитория:

```bash
python -m venv .venv
# Windows Git Bash:
source .venv/Scripts/activate
pip install -r requirements.txt
```

Скопируйте `src/.env.example` в `src/.env` и вставьте ключи
`OPENROUTER_API_KEY`, `JINA_API_KEY`. Файл `.env` игнорируется Git.

Запустите Qdrant через Docker:

```bash
docker run --rm --name rag-qdrant -p 6333:6333 -v rag_qdrant_data:/qdrant/storage qdrant/qdrant:latest
```

## Индексация

```bash
python src/main.py index
# Явная переиндексация (удаляет прежнюю коллекцию):
python src/main.py index --recreate --max-tokens 250 --batch-size 16
```

Размерность embedding определяется автоматически. При смене embedding-модели
индекс необходимо пересоздать с `--recreate`. Чанки не пересекают границы
глав или стихов; одиночный слишком длинный стих сохраняется целиком.

## Поиск и генерация

```bash
python src/main.py ask "Что Библия говорит о прощении?"
python src/main.py chat
python src/main.py ask "Кто такой Моисей?" --top-k 30 --top-n 5
python src/main.py ask "Кто такой Моисей?" --no-rerank
```

Для диалога используйте `exit`. Режим `--no-rerank` не требует
`JINA_API_KEY`. Обе модели на OpenRouter могут иметь лимиты и временную
недоступность, особенно при использовании бесплатных вариантов.

## Проверки

```bash
python -m compileall -q src
python -m unittest discover -s tests -v
```
