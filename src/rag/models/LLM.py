from openai import OpenAI
from ..config import OPENROUTER_API_KEY

class Model:

    def __init__(self):
        self.client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        )


    def answer(self, query, documents):
        response = self.client.chat.completions.create(
        model="nvidia/nemotron-3.5-super-vl:free",
        messages=[
                {
                    "role": "user",
                    "content": query
                },
                {
                    'role': 'assistant',
                    'content': '|||'.join(documents)
                }
                ],
        extra_body={"reasoning": {"enabled": True}}
        )

        response = response.choices[0].message

        return response.content

