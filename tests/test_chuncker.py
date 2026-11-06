import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rag.chuncker import Chuncker


class WordTokenizer:
    def encode(self, text):
        return text.split()


class ChunckerTests(unittest.TestCase):
    def setUp(self):
        self.chunker = Chuncker(tokenizer=WordTokenizer())

    def test_no_lost_verses_and_final_flush(self):
        rows = [
            {"book": "Genesis", "chapter": 1, "verse": i, "text": str(i)}
            for i in range(1, 6)
        ]
        chunks = self.chunker.get_chuncks(rows, max_length=2)
        self.assertEqual(
            [chunk["text"] for chunk in chunks],
            ["1\n2", "3\n4", "5"],
        )
        self.assertEqual(
            [(c["verse_start"], c["verse_end"]) for c in chunks],
            [("1", "2"), ("3", "4"), ("5", "5")],
        )

    def test_boundaries_and_reset(self):
        rows = [
            {"book": "A", "chapter": 1, "verse": 1, "text": "one"},
            {"book": "A", "chapter": 2, "verse": 1, "text": "two"},
            {"book": "B", "chapter": 1, "verse": 1, "text": "three"},
        ]
        self.assertEqual(
            [c["text"] for c in self.chunker.get_chuncks(rows, 100)],
            ["one", "two", "three"],
        )
        self.assertEqual(len(self.chunker.get_chuncks(rows[:1], 100)), 1)

    def test_long_single_verse(self):
        rows = [
            {"book": "A", "chapter": 1, "verse": 1, "text": "a b c"},
            {"book": "A", "chapter": 1, "verse": 2, "text": "d"},
        ]
        self.assertEqual(
            [c["text"] for c in self.chunker.get_chuncks(rows, 2)],
            ["a b c", "d"],
        )

    def test_empty_input_and_bad_limit(self):
        self.assertEqual(self.chunker.get_chuncks([], 250), [])
        with self.assertRaises(ValueError):
            self.chunker.get_chuncks([], 0)


if __name__ == "__main__":
    unittest.main()
