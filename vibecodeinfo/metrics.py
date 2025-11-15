from prometheus_client import Counter


news_insert_total = Counter(
    "news_insert_total",
    "Total number of news inserted into DB"
)

news_insert_errors_total = Counter(
    "news_insert_errors_total",
    "Number of errors during news insertion"
)


llm_requests_total = Counter(
    "llm_requests_total",
    "Total number of LLM requests"
)

llm_request_errors_total = Counter(
    "llm_request_errors_total",
    "Number of errors while calling LLM"
)

published_posts_total = Counter(
    "published_posts_total",
    "Total number of published news posts"
)
