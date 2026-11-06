"""Chunk scripture without losing verses or crossing chapter boundaries."""
from .models.tokenizer import Tokenizer


class Chuncker:
    """Preserve original public spelling for compatibility."""

    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()
        self.chuncks = []

    def get_chuncks(self, data, max_length=250):
        if max_length < 1:
            raise ValueError("max_length должен быть положительным.")
        rows = data.to_dict("records") if hasattr(data, "to_dict") else data
        chunks = []
        current = None
        for row in rows:
            book = str(row["book"])
            chapter = int(row["chapter"])
            raw_text = row["text"]
            if raw_text is None or not str(raw_text).strip():
                continue
            verse_text = str(raw_text).strip()
            verse = row.get("verse")
            verse = str(verse) if verse is not None else None
            if current is not None:
                proposed = current["text"] + "\n" + verse_text
                boundary = (current["book"] != book or current["chapter"] != chapter)
                too_long = len(self.tokenizer.encode(proposed)) > max_length
                if boundary or too_long:
                    chunks.append(current)
                    current = None
            if current is None:
                current = {"book": book, "chapter": chapter, "text": verse_text}
                if verse is not None:
                    current["verse_start"] = verse
                    current["verse_end"] = verse
            else:
                current["text"] += "\n" + verse_text
                if verse is not None:
                    current["verse_end"] = verse
        if current is not None:
            chunks.append(current)
        self.chuncks = chunks
        return chunks

    def get_chunks(self, data, max_length=250):
        return self.get_chuncks(data, max_length)


Chunker = Chuncker
