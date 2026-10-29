from email import header
from urllib import request
import requests
from bs4 import BeautifulSoup
import re
import time
import asyncio
from aiohttp import ClientSession
import aiohttp

# 1. Добавить обработку ошибок. Использовать 
# response.raise_for_status() для проверки HTTP-статуса и try/except для обработки сетевых ошибок.
# 2. Улучшить обработку ссылок и HTML.
# - Использовать urljoin() для формирования URL.
# - Проверять match is None перед match.group().
# - Проверять, найден ли HTML-элемент перед вызовом find_all().

st_accept = "text/html" 
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
"Accept": st_accept,
"User-Agent": st_useragent
}


def get_content(soup):
    text = soup.body.find(class_ = "document-page__content document-page_left-padding")
    p_s = text.find_all('p')
    content = '\n'.join(p.get_text(' ', strip = True) for p in p_s)
    return content

async def get_info(link, session, semaphore):
    async with semaphore:
        url = 'https://www.consultant.ru/' + link['href']
        try:
            async with session.get(url) as response:

                tree = await response.text()
                soup_tree = BeautifulSoup(tree, 'lxml')

                pattern = r"Статья\s+(\d+(?:\.\d+)?)\.\s*(.+)"
                match = re.search(pattern, link.text)
                number = match.group(1) 
                title = match.group(2)  
                content = get_content(soup_tree)

                res = {
                            'number':number,
                            'title':title,
                            'text':content
                        }
                
                return res
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))
            return None

        except aiohttp.ClientResponseError as e:
            print('Status:', str(e.status))
            return None

async def main():

    async with ClientSession(headers=headers) as session:
        try:
            async with session.get("https://www.consultant.ru/document/cons_doc_LAW_10699/") as request:

                src = await request.text()


                soup = BeautifulSoup(src, 'lxml')
                links = soup.body.find(class_="document-page__toc")
                links = links.find_all('a')

                semaphore = asyncio.Semaphore(10)

                tasks = []

                for idx in range(len(links)):
                    if 'статья' not in links[idx].text.lower():
                        continue

                    tasks.append(get_info(links[idx], session, semaphore)) 
                    

                tasks = await asyncio.gather(*tasks)

                articles = [task for task in tasks if task is not None]

                return articles
        except aiohttp.ClientConnectorError as e:
            raise e
        except aiohttp.ClientResponseError as e:
            raise e


if __name__ == '__main__':
    start = time.time()
    result = asyncio.run(main())
    end = time.time()
    print(result[-1])
    print(len(result))
    print(f'{end-start:.2f}')

