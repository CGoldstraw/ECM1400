# Copyright 2021 Charles Goldstraw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

"""Handles requesting, filtering and formatting recent news articles.

Uses newsapi.org to request top headlines, and filters them based on
search terms defined in the config file. Creation and deletion of
scheduled updates is also implemented.
"""
import time
import sched
import logging
from datetime import datetime
import requests
from flask import Markup
from config_handler import read_config

news_articles = []
blocked_articles = []
news_updates = {}
s = sched.scheduler(time.time, time.sleep)


def filter_articles(
        articles: list[dict], search_terms: str) -> list[dict]:
    """Returns all articles containing a given search term in them.

    Takes a list of articles and filters them by their title, only
    returning articles that contain at least one of the search terms in
    their title.

    Args:
        articles: A list of news articles.
        search_terms: A space separated string of search terms.

    Returns:
        A list containing only the articles with titles that contained
        a search term.
    """
    relevant_articles = []
    for article in articles:
        title = article["title"].lower()
        if any(term.lower() in title for term in search_terms.split()):
            relevant_articles.append(article)
    return relevant_articles


def news_API_request(
        covid_terms: str = "Covid COVID-19 coronavirus") -> list[dict]:
    """Requests recent filtered top headlines from newsapi.org.

    Sends an API request to newsapi.org, filter the articles by the
    given terms and return the filtered articles.

    Args:
        covid_terms: Space separated terms to search news articles for.

    Returns:
        A list of news articles, with titles containing at least one
        search term.
    """
    logging.info("Requesting recent top headlines...")
    country, api_key = read_config("news_country_code", "news_API_key")

    parameters = f"?country={country}&apiKey={api_key}"
    url = "https://newsapi.org/v2/top-headlines" + parameters
    response = requests.get(url)

    filtered_articles = []
    if api_key == "[API_KEY_HERE]":
        logging.critical("The news API key has not been set in config.json")
        raise ValueError("The news API key has not been set in config.json")

    articles = response.json()['articles']
    filtered_articles = filter_articles(articles, covid_terms)

    if len(filtered_articles) == 0:
        empty_article = {}
        empty_article["title"] = "No relevant articles currently"
        empty_article["content"] = ""
        filtered_articles.append(empty_article)

    return filtered_articles


def format_article(article: dict[str]) -> dict[str]:
    """Shortens an article's contents and removes unnecessary data.

    Format an article for the data structure used on the website by
    removing unnecessary data, shortens the contents to 20 words and
    adds a link to the article in the article's contents.

    Args:
        article: The news article to format.

    Returns:
        The new shortened article.
    """
    formatted_article = {}
    formatted_article["title"] = article["title"]
    url = f"<a href='{article['url']}'>[Click Here]</a>"
    if article["content"]:
        description = " ".join(article["content"].split()[:20])
        content = f"{description}... {url}"
        formatted_article["content"] = Markup(content)
    else:
        formatted_article["content"] = Markup(url)

    return formatted_article


def update_news(update_name: str = None) -> None:
    """Updates a list of relevant articles with the news API.

    Gathers and formats recent top headlines, adds new unblocked
    headlines to the stored articles. If the update was scheduled,
    the update is either removed or repeated.

    Args:
        update_name (Optional): The identifier of the update.
    """
    search_terms, interval = read_config(
        "news_search_terms","news_update_interval_seconds")
    api_articles = news_API_request(search_terms)

    for article in api_articles:
        formatted_article = format_article(article)
        if formatted_article not in news_articles and \
                formatted_article["title"] not in blocked_articles:
            # As the article isn't repeated or blocked, it can be added
            logging.info("Article '%s' added.", article['title'])
            news_articles.append(formatted_article)

    if update_name in news_updates:
        # The current update belongs to a scheduled update, so either
        # repeat or delete it depending on whether it is set to repeat.
        logging.info("News update '%s' completed.", update_name)
        if news_updates[update_name]["repeats"]:
            schedule_news_updates(interval, update_name)
            repeat_log = "News update '%s' scheduled to repeat."
            logging.info(repeat_log, update_name)
        else:
            news_updates.pop(update_name)
            logging.info("News update '%s' removed.", update_name)
    elif update_name:
        logging.warning("Update '{update_name}' does not exist.")
    else:
        logging.info("News articles updated.")


def block_article(title: str) -> None:
    """Removes and blocks a news article.

    Adds an article title to the blocked articles to hide the article
    and removes the article from the stored articles.

    Args:
        title: The title of the article to block.
    """
    blocked_articles.append(title)
    for index, article in enumerate(news_articles):
        if title == article["title"]:
            news_articles.pop(index)

    logging.info("Article '%s' blocked.", title)


def create_news_update(
        update_time: str, update_name: str, repeats: str) -> None:
    """Create and schedule a news update for a given time in HH:MM.

    Creates a new update with a given name and repeating information,
    calculates seconds difference between the current time the update
    time, then schedules an update with that delay.

    Args:
        update_time: Time of the update in HH:MM.
        update_name: The identifier of the update.
        repeats: Either None or "repeat".
    """
    update = {"time": update_time, "repeats": repeats}
    news_updates[update_name] = update

    schedule_time = datetime.strptime(update_time, "%H:%M")
    current_time = datetime.now()
    seconds = (schedule_time - current_time).seconds
    schedule_news_updates(seconds, update_name)

    log_message = "%s news update '%s' created for %s."
    repeating = "Repeating" if repeats else "Single"
    logging.info(log_message, repeating, update_name, update_time)


def schedule_news_updates(
        update_interval: int, update_name: str) -> None:
    """Schedules a news update in a specified number of seconds.

    Calls a news update in a specified number of seconds, and creates a
    new update if the identifier is not found.

    Args:
        update_interval: The number of seconds until the update.
        update_name: The identifier of the update.
    """
    if update_name not in news_updates:
        news_updates[update_name] = {"time": "None", "repeats": None}
        logging.warning("Update not found, dummy update created.")

    update = s.enter(update_interval, 1, update_news, update_name)
    news_updates[update_name]["update"] = update
