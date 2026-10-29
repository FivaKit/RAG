
import asyncio
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin
import logging
import aiohttp
from bs4 import BeautifulSoup


class Parser:

    logger = logging.getLogger(__name__)
    BASE_URL = "https://www.consultant.ru/"
    INDEX_URL = urljoin(BASE_URL, "document/cons_doc_LAW_10699/")
    HEADERS = {
                "Accept": "text/html",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/15.4 Safari/605.1.15"
                )
            }
    
    ARTICLE_PATTERN = re.compile(
            r"^Статья\s+(\d+(?:\.\d+)*)\.\s*(.+)$",
            flags=re.IGNORECASE
        )

    
    def __init__(self, MAX_CONCURRENT=5):
    # Настройки
        self.MAX_CONCURRENT = MAX_CONCURRENT
        

    # Извлечение ссылок на статьи
    def extract_article_links(self, html):
        soup = BeautifulSoup(html, "lxml")

        toc = soup.select_one(".document-page__toc")

        if toc is None:
            raise ValueError("Не найдено оглавление документа")

        articles = []
        seen = set()

        for link in toc.select("a[href]"):
            name = link.get_text(" ", strip=True)
            match = self.ARTICLE_PATTERN.match(name)

            if match is None:
                continue

            number, title = match.groups()

            if number in seen:
                continue

            seen.add(number)

            articles.append({
                "number": number,
                "title": title,
                "url": urljoin(self.BASE_URL, link["href"])
            })

        if not articles:
            raise ValueError("В оглавлении не найдены статьи")

        return articles


    # Извлечение текста статьи
    @staticmethod
    def extract_content(html):
        soup = BeautifulSoup(html, "lxml")

        content_block = soup.select_one(
            ".document-page__content.document-page_left-padding"
        )

        if content_block is None:
            raise ValueError("Не найден блок с текстом статьи")

        paragraphs = content_block.find_all("p")

        content = "\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )

        if not content:
            raise ValueError("Текст статьи пуст")

        return content


    # Асинхронная загрузка HTML
    async def fetch_html(self, url, session, semaphore):
        async with semaphore:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()


    # Получение одной статьи
    async def fetch_article(self, article, session, semaphore):
        url = article["url"]

        try:
            html = await self.fetch_html(url, session, semaphore)
            content = self.extract_content(html)

            return {
                "number": article["number"],
                "title": article["title"],
                "text": content
            }, None

        except aiohttp.ClientResponseError as e:
            error = f"HTTP {e.status}: {e.message}"

        except asyncio.TimeoutError:
            error = "Превышено время ожидания"

        except aiohttp.ClientError as e:
            error = f"{type(e).__name__}: {e}"

        except (ValueError, UnicodeError) as e:
            error = f"Ошибка обработки HTML: {e}"

        return None, {
            "number": article["number"],
            "url": url,
            "error": error
        }


    # Основная функция
    async def parse(self):
        timeout = aiohttp.ClientTimeout(
            total=20,
            connect=5,
            sock_read=15
        )

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        async with aiohttp.ClientSession(
            headers=self.HEADERS,
            timeout=timeout
        ) as session:

            # Получаем оглавление
            html = await self.fetch_html(
                self.INDEX_URL, session, semaphore
            )

            links = self.extract_article_links(html)

            self.logger.info(f"Найдено статей: {len(links)}")

            # Создаём корутины
            tasks = [
                self.fetch_article(article, session, semaphore)
                for article in links
            ]

            # Выполняем запросы конкурентно
            results = await asyncio.gather(*tasks)

        # Разделяем успешные результаты и ошибки
        articles = [
            article
            for article, error in results
            if article is not None
        ]

        errors = [
            error
            for article, error in results
            if error is not None
        ]

        return articles, errors


if __name__ == "__main__":
    start = time.perf_counter()

    parser = Parser()

    try:
        articles, errors = asyncio.run(parser.parse())

    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
        print(f"Не удалось получить оглавление: {e}")

    else:
        # Сохраняем успешно загруженные статьи
        if articles:
            Path("articles.json").write_text(
                json.dumps(articles, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

        # Сохраняем ошибки
        Path("errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Успешно загружено: {len(articles)}")
        print(f"Ошибок: {len(errors)}")

        if articles:
            print(articles[-1])

    finally:
        print(f"Время выполнения: {time.perf_counter() - start:.2f} с")
