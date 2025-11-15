import aiohttp
import os
from vibecodeinfo.dto import NewsDTO
from vibecodeinfo.logger import logger
from vibecodeinfo.metrics import llm_requests_total, llm_request_errors_total
import json


class ChutesGPTClient:
    url = "https://llm.chutes.ai/v1/chat/completions"
    api_token = os.getenv("CHUTES_API_TOKEN", default='')
    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json"
    }
    model = "openai/gpt-oss-20b"
    max_tokens = 1024
    temperature = 0.7

    async def is_duplicate(self, new_news: NewsDTO, old_news_list: list[NewsDTO]) -> bool:
        # todo: починить и убрать заглушку
        old_news_titles = [news.title for news in old_news_list]
        return new_news.title in old_news_titles

        logger.info(f"Проверка новости '{new_news.title}' на уникальность")

        old_news_text = [f'{old_news.title} {old_news.description}' for old_news in old_news_list]
        logger.debug(f"Старых новостей: {len(old_news_text)}")
        prompt = f"""
                    Новая новость:
                        {new_news.title} {new_news.description}
                    Старые новости:
                        {'; '.join(old_news_text)}
                    Ответь строго в формате JSON:
                    {{
                      "is_duplicate": true/false,
                      "reason": "краткое объяснение"
                    }}
                    Не добавляй ничего, кроме JSON.
                """
        logger.debug(f"Запрос: {prompt}")
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты — ассистент, который помогает определить, "
                        "дублирует ли новая новость уже существующие."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        llm_requests_total.inc()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.url,
                    headers=self.headers,
                    json=body
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = json.loads(data['choices'][0]['message']['content'])
                    logger.debug(f"Ответ: {result}")
                    logger.info(
                        f"""Новость '{new_news.title}'
                            определена как {'дубликат' if result['is_duplicate'] else 'уникальная'}
                            Обоснование: {result['reason']}
                        """
                    )
                    return result
                else:
                    llm_request_errors_total.inc()
                    raise Exception(f"Ошибка {response.status} при обработке запроса к LLM")
