from sqlalchemy import select
from vibecodeinfo.dto import NewsDTO
from vibecodeinfo.db.models import News
from datetime import timedelta, datetime
from vibecodeinfo.db.init_db import async_session_maker
from vibecodeinfo.metrics import news_insert_total, news_insert_errors_total


async def get_news(delta: timedelta) -> list[NewsDTO]:
    now_datetime = datetime.now()
    async with async_session_maker() as session:
        result = await session.execute(
            select(News).where(News.created_at >= now_datetime - delta)
        )
        news_list = []
        for news in result.scalars().all():
            news_list.append(
                NewsDTO(
                    title=news.title,
                    description=news.description,
                    source=news.source
                )
            )
        return news_list


async def add_news(news: NewsDTO) -> None:
    try:
        async with async_session_maker() as session:
            news_model = News(title=news.title, description=news.description, source=news.source)
            session.add(news_model)
            await session.commit()
            await session.refresh(news)
            news_insert_total.inc()
    except Exception:
        news_insert_errors_total.inc()
        raise


async def add_news_list(news_list: list[NewsDTO]) -> None:
    try:
        async with async_session_maker() as session:
            for news in news_list:
                news_model = News(
                    title=news.title,
                    description=news.description,
                    source=news.source
                )

                session.add(news_model)
            await session.commit()
            news_insert_total.inc(len(news_list))
    except Exception:
        news_insert_errors_total.inc()
        raise
