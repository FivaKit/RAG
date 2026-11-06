"""Tokenizer used to estimate chunk length."""
from ..config import TOKENIZER_MODEL


class Tokenizer:
    def __init__(self, model_name=TOKENIZER_MODEL):
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def encode(self, text):
        return self.tokenizer.encode(str(text), add_special_tokens=False)
