from vibecodeinfo.news import NewsFinder


def test__extract_news__returns_correct_news_object(newsapi_success_response, news):
    assert NewsFinder._extract_news(newsapi_success_response) == [news]
