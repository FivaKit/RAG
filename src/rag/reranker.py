import json
import requests
import os
from config import JINA_API_KEY

class Reranker:
    def __init__(self):
        self.url = "https://api.jina.ai/v1/rerank"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {JINA_API_KEY}"
        }

    def rerank(self, query, documents, top_n):

        payload = {
            "model": "jina-reranker-v3.5",
            "query": query,
            "top_n": top_n,
            "documents": documents,
            "return_documents": True
        }

        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()['results']
        return [el['document']['text'] for el in result]
    
# reranker = Reranker()
# query = "Как приготовить варенье?"

# documents = [
#     "Вкусное варенье.",
#     "Холодец готовится, варенье намазывается.",
#     "Чтобы приготовить варенье, нужно взять ягоды, сахар и воду. Ягоды засыпают сахаром и варят на медленном огне.",
#     "Как приготовить борщ: сначала сварите мясной бульон.",
#     "Варенье из клубники — сладкий десерт."
# ]

# # print(reranker.rerank(query, documents, 3))
# print(reranker.rerank(query, documents, 3))

