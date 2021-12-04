from covid_news_handling import filter_articles
from covid_news_handling import news_API_request
from covid_news_handling import format_article
from covid_news_handling import update_news
from covid_news_handling import create_news_update
from covid_news_handling import schedule_news_updates


def test_filter_articles():
    articles = []
    articles.append({"title": "Irrelevant article"})
    articles.append({"title": "Unrelated article"})
    articles.append({"title": "Important information!"})
    assert len(filter_articles(articles, "Important")) == 1
    assert len(filter_articles(articles, "Article")) == 2
    assert len(filter_articles(articles, "Irrelevant Important")) == 2


def test_news_API_request():
    request = news_API_request()
    assert request
    assert news_API_request('Covid COVID-19 coronavirus') == request
    blank_request = news_API_request("zyxwvu")
    assert len(blank_request) == 1
    empty_phrase = "No relevant articles currently"
    assert blank_request[0]["title"] == empty_phrase


def test_format_article():
    article = {"title": "Test", "url": "https://google.co.uk"}
    article["content"] = "Test "*50
    formatted_content = format_article(article)["content"].split()
    assert len(formatted_content) <= 25


def test_update_news():
    update_news('test')


def test_create_news_update():
    create_news_update("00:00", "Test", None)


def test_schedule_news_updates():
    schedule_news_updates(
        update_interval=10, update_name='update test')
