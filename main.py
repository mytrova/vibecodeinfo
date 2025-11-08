import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import os
from news import NewsFinder, news_to_html, News
from datetime import timedelta


CHANNEL = os.getenv("CHANNEL")
POST_INTERVAL_HOURS = 24
THEMES = ['vibecode', 'Vibe coding', 'Vibecoding', 'вайбкодинг']

bot = Bot(token=os.getenv("BOT_TOKEN", ''))
dp = Dispatcher()
router = Router()
dp.include_router(router)
news_finder = NewsFinder()


async def main() -> None:
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


@router.message(F.text == "День")
async def show_day_news(message: Message) -> None:
    await response(message, news_finder.find(themes=THEMES, delta=timedelta(days=1)))


@router.message(F.text == "Неделя")
async def show_week_news(message: Message) -> None:
    await response(message, news_finder.find(themes=THEMES, delta=timedelta(weeks=1)))


@router.message(F.text == "Месяц")
async def show_month_news(message: Message) -> None:
    await response(message, news_finder.find(themes=THEMES, delta=timedelta(weeks=4)))


async def response(message: Message, news_list: list[News]) -> None:
    if not news_list:
        await message.answer(text="Нет свежих новостей")
        return

    for news in news_list:
        await message.answer(
            parse_mode="HTML",
            text=news_to_html(news)
        )


if __name__ == "__main__":
    asyncio.run(main())
