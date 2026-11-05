from rag.chuncker import Chuncker
import pandas as pd


if __name__ == '__main__':
    data = pd.read_csv('src/data.csv')
    chuncker = Chuncker()
    print(data.head(2))
    # chuncks = chuncker.get_chuncks