from transformers import AutoTokenizer

class Tokenizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
        "nvidia/Nemotron-3.5-Embed-1B-BF16"
        )
    
    def encode(self, text):
        tokens = self.tokenizer.encode(
            text,
            add_special_tokens = False
        )
        return tokens
