from openai import OpenAI
from ..config import OPENROUTER_API_KEY


class Embedder:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            timeout=180,
            max_retries=3
        )

    def encode(self, input, batch_size=16):
        if isinstance(input, str):
            input = [input]

        vectors = []

        for start in range(0, len(input), batch_size):
            output = self.client.embeddings.create(
                model="liquid/lfm-2.5-embedding-350m:free",
                input=input[start:start + batch_size],
                encoding_format="float"
            )

            vectors.extend(
                item.embedding
                for item in sorted(output.data, key=lambda x: x.index)
            )

        return vectors