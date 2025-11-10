from newsapi import NewsApiClient
import os
from datetime import datetime, timedelta
import dataclasses
from aiogram.utils.markdown import hbold, hlink


@dataclasses.dataclass()
class News:
    title: str
    description: str
    source: str


def news_to_html(news: News) -> str:
    return f"""{hbold(news.title)}\n
            {news.description}\n
            {hlink('источник', news.source)}"""


class NewsFinder:
    def __init__(self) -> None:
        self.newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY", ''))

    def find(self, themes: list[str], delta: timedelta) -> list[News]:
        result = []
        now_date = datetime.now().date()
        for theme in themes:
            data = self.newsapi.get_everything(q=theme,
                                               from_param=now_date - delta,
                                               to=now_date,
                                               language='ru',
                                               sort_by='relevancy')
            result.extend(self._extract_news(data))
        return result

    @staticmethod
    def _extract_news(data: dict) -> list[News]:
        result = []

        for article in data['articles']:
            result.append(
                News(
                    title=article['title'],
                    description=article['description'],
                    source=article['url']
                )
            )
        return result
