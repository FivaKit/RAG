from rag.models.tokenizer import Tokenizer

class Chuncker:
    def __init__(self):
        self.chuncks = []
        self.tokenizer = Tokenizer()

    def get_chuncks(self, data, max_length):
        chunck = {}
        for i in range(len(data)):
            if 'text' not in chunck:
                chunck['book'] = data.iloc[i]['book']
                chunck['chapter'] = data.iloc[i]['chapter'].item()
                chunck['text'] = data.iloc[i]['text']
                continue
            if len(self.tokenizer.encode(chunck['text'])) > max_length or chunck['book']!=data.iloc[i]['book'] or chunck['chapter']!=data.iloc[i]['chapter']:
                self.chuncks.append(chunck)
                chunck = {}
                continue
            chunck['text'] += data.iloc[i]['text']
        return self.chuncks


