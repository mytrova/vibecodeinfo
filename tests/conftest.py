import pytest
from vibecodeinfo.news import News


@pytest.fixture
def title():
    return "ИИ-разработчик потребовал отпуск и кофе"


@pytest.fixture
def description():
    return """Компания DeepLazyTech запустила ИИ, пишущий код быстрее людей.
              Через день он сам создал баг, открыл тикет 'починить позже'
              и ушёл в цифровой отпуск."""


@pytest.fixture
def source():
    return 'http://www.news.info'


@pytest.fixture
def news(title, description, source):
    return News(
        title=title,
        description=description,
        source=source
    )


@pytest.fixture
def newsapi_success_response(title, description, source):
    return {
        'articles': [
            {
                'title': title,
                'description': description,
                'url': source
            }
        ],
    }
