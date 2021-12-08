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

"""Handles formatting, creating, and deleting updates.

Combines the separate COVID and news update lists, and formats them for
the website. Also adds and removes updates from these lists after
user events from the dashboard.
"""
import logging
from flask import request
import covid_data_handler as cdh
import covid_news_handling as cnh

updates = []


def format_update(update: dict[str], covid: bool, news: bool) -> str:
    """Generates a string describing an update for the website.

    Args:
        update: A dictionary containing update information.
        covid: If True, the update affects COVID data.
        news: If True, the update affects news articles.

    Returns:
        A string containing the time of the update, the data updated,
        and whether the update repeats or not.

    Examples:
        >>> update = {"time": "01:23", "repeats": "repeat"}
        >>> format_update(update, True, True)
        "01:23, Updates Covid & News, Repeats"

        >>> update = {"time": "12:34", "repeats": None}
        >>> format_update(update, False, True)
        "12:34, Updates News, Doesn't Repeat"
    """
    data = [update["time"]]
    # Make list of items being updated, to be joined with "&".
    updated_data = ["Covid"*covid, "News"*news]
    updated_data = filter(None, updated_data)
    # Gives "Updates Covid", "Updates News", or "Updates Covid & News"
    data.append("Updates " + " & ".join(updated_data))
    data.append("Repeats" if update["repeats"] else "Doesn't Repeat")
    return ", ".join(data)


def format_updates() -> None:
    """Combine the COVID and news updates into a list.

    Convert the separate update dictionaries into a formatted list
    of updates with titles and contents for the website to render.
    """
    updates.clear()
    all_updates = {**cdh.covid_updates, **cnh.news_updates}
    for name, update in all_updates.items():
        if name not in updates:
            is_covid = name in cdh.covid_updates
            is_news = name in cnh.news_updates
            content = format_update(update, is_covid, is_news)
            update = {"title": name, "content": content}
            updates.append(update)


def create_update(sched_time: str) -> None:
    """Creates new COVID and news updates.

    Uses the parameters in the URL to create updates for COVID data and
    news articles at a given time, with an optional repeating feature.

    Args:
        sched_time: The time of the update in HH:MM format.
    """
    name = request.args.get("two")
    update_covid = request.args.get("covid-data")
    update_news = request.args.get("news")
    repeats = request.args.get("repeat")
    # Ensure unique name
    if name not in {**cdh.covid_updates, **cnh.news_updates}:
        if update_covid:
            cdh.create_covid_update(sched_time, name, repeats)
        if update_news:
            cnh.create_news_update(sched_time, name, repeats)
        if not update_covid and not update_news:
            logging.warning("Empty update created, request ignored.")
    else:
        logging.warning("Update name already exists.")


def remove_update(name: str) -> None:
    """Removes COVID and News updates.

    Removes an update, specified by its name, by cancelling the next
    scheduled event and removing the update from the dictionaries.

    Args:
        name: The identifier of the update.
    """
    if name in cdh.covid_updates:
        cdh.s.cancel(cdh.covid_updates[name]["update"])
        cdh.covid_updates.pop(name)
        logging.info("COVID update '%s' removed.", name)

    if name in cnh.news_updates:
        cnh.s.cancel(cnh.news_updates[name]["update"])
        cnh.news_updates.pop(name)
        logging.info("News update '%s' removed.", name)
