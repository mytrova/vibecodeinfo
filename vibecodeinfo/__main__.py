import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import os
from vibecodeinfo.news import NewsFinder, news_to_html, NewsProcessor
from vibecodeinfo.dto import NewsDTO
from datetime import timedelta
from vibecodeinfo.db.crud import get_news
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from vibecodeinfo.logger import logger
from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from aiogram.client.default import DefaultBotProperties
import time
from vibecodeinfo.metrics import published_posts_total
from prometheus_client import start_http_server


CHANNEL = os.getenv("CHANNEL", '')
bot = Bot(
    token=os.getenv("BOT_TOKEN", ''),
    default=DefaultBotProperties(parse_mode="HTML")

)
dp = Dispatcher()
router = Router()
dp.include_router(router)
news_finder = NewsFinder()
news_processor = NewsProcessor()
scheduler = AsyncIOScheduler()
UPDATE_HOURS = 1


async def metrics(request: web.Request) -> web.Response:
    return web.Response(
        body=generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )


async def run_metrics_server() -> None:
    app = web.Application()
    app.router.add_get("/metrics", metrics)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8001)
    await site.start()


async def update_news() -> None:
    news_list = news_finder.find(delta=timedelta(hours=UPDATE_HOURS))
    logger.info(f"За {UPDATE_HOURS} часов найдено {len(news_list)} новостей")
    news_to_publish = await news_processor.add_news_to_db_if_unique(news_list=news_list)
    if news_to_publish:
        for news_item in news_to_publish:
            message = news_to_html(news_item)
            await bot.send_message(CHANNEL, message)
            published_posts_total.inc()
            logger.info(f"Новость {news_item.title} опубликована в канал")
            time.sleep(60)


async def main() -> None:
    await asyncio.create_task(run_metrics_server())
    start_http_server(9000)
    scheduler.add_job(update_news, IntervalTrigger(hours=UPDATE_HOURS), id="update_news")
    scheduler.start()
    logger.info(f"Scheduler запущен с интервалом в {UPDATE_HOURS} часов")
    await dp.start_polling(bot)


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    text = "Привет! Хочешь свежие новости по теме вайбкодинга? За какой период поискать?"

    kb = [
        [
            KeyboardButton(text="День"),
            KeyboardButton(text="Неделя"),
            KeyboardButton(text="Месяц"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "/update")
async def update(message: Message) -> None:
    await update_news()
    await message.answer(text="Готово!")


@router.message(F.text == "/init")
async def init(message: Message) -> None:
    news_list = news_finder.find(delta=timedelta(weeks=4))
    logger.info(f"Найдено {len(news_list)} новостей")
    news_to_publish = await news_processor.add_news_to_db_if_unique(news_list=news_list)
    logger.info(f"Готово к публиковке {len(news_to_publish)} уникальных новостей")
    if news_to_publish:
        for news_item in news_to_publish:
            news_html = news_to_html(news_item)
            await bot.send_message(CHANNEL, news_html)
            logger.info(f"Новость {news_item.title} опубликована в канал")

    await message.answer(text="Готово!")


@router.message(F.text == "День")
async def show_day_news(message: Message) -> None:
    news = await get_news(delta=timedelta(days=1))
    await response(message, news)


@router.message(F.text == "Неделя")
async def show_week_news(message: Message) -> None:
    news = await get_news(delta=timedelta(weeks=1))
    await response(message, news)


@router.message(F.text == "Месяц")
async def show_month_news(message: Message) -> None:
    news = await get_news(delta=timedelta(weeks=4))
    await response(message, news)


async def response(message: Message, news_list: list[NewsDTO]) -> None:
    if not news_list:
        await message.answer(text="Нет свежих новостей")
        return

    for news in news_list:
        await message.answer(
            text=news_to_html(news)
        )


if __name__ == "__main__":
    asyncio.run(main())
