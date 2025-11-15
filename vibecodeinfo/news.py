from newsapi import NewsApiClient
import os
from datetime import datetime, timedelta
from aiogram.utils.markdown import hbold, hlink
from vibecodeinfo.llm_client import ChutesGPTClient
from vibecodeinfo.db.crud import get_news, add_news_list
from vibecodeinfo.dto import NewsDTO
from vibecodeinfo.logger import logger


def news_to_html(news: NewsDTO) -> str:
    return f"""{hbold(news.title)}\n
            {news.description}\n
            {hlink('источник', news.source)}"""


class NewsFinder:
    THEMES = ['vibecode', 'Vibe coding', 'Vibecoding', 'вайбкодинг']

    def __init__(self) -> None:
        self.newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY", ''))

    def find(self, delta: timedelta) -> list[NewsDTO]:
        result = []
        now = datetime.now()
        for theme in self.THEMES:
            data = self.newsapi.get_everything(q=theme,
                                               from_param=now - delta,
                                               to=now,
                                               language='ru',
                                               sort_by='relevancy')
            result.extend(self._extract_news(data))
        return result

    @staticmethod
    def _extract_news(data: dict) -> list[NewsDTO]:
        result = []

        for article in data['articles']:
            result.append(
                NewsDTO(
                    title=article['title'],
                    description=article['description'],
                    source=article['url'],
                )
            )
        return result


class NewsProcessor:
    last_news_delta = timedelta(weeks=4)

    async def add_news_to_db_if_unique(self, news_list: list[NewsDTO]) -> list[NewsDTO]:
        last_news = await get_news(self.last_news_delta)
        llm_client = ChutesGPTClient()
        news_to_add: list[NewsDTO] = []
        for news in news_list:
            old_news_list = last_news + news_to_add
            is_duplicate = await llm_client.is_duplicate(
                new_news=news,
                old_news_list=old_news_list
            )
            if is_duplicate:
                continue
            news_to_add.append(news)

        if not news_to_add:
            logger.info("Нет уникальных новостей для добавления в базу")
            return []

        await add_news_list(news_to_add)
        logger.info(f"В базу добавлено {len(news_to_add)} новостей")

        return news_to_add
