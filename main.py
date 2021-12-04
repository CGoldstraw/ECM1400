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

"""Renders recent news articles and COVID data to a dashboard template.

Uses flask to host a dashboard displaying recent COVID data and news
articles, with the COVID data location and news search terms decided by
the user in the config file. Calls events to be handled such as
scheduling of updates, removal of updates, and removal of news articles.
"""
import logging
from flask import Flask, render_template, request
from config_handler import read_config
import covid_data_handler as cdh
import covid_news_handling as cnh
import update_handler

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filename='sys.log',
    encoding='utf-8')

app = Flask(__name__)
# Get initial COVID data.
ltla, nation = read_config("covid_local", "covid_nation")
cdh.covid_API_request(location=ltla, location_type="ltla")
cdh.covid_API_request(location=nation, location_type="nation")
# Get initial news articles.
cnh.update_news()


@app.route('/')
@app.route('/index')
def index() -> str:
    """Handles events and renders recent news and COVID data.

    Checks URL parameters for events (creating and deleting updates,
    and blocking news articles), runs the schedulers to check for any
    scheduled updates, formats pending updates for the website,
    refreshes COVID data and news articles, and renders the template
    with the current data.

    Returns:
        The html template rendered with the most recent data."""
    # Event Management
    if (sched_time := request.args.get("update")):
        update_handler.create_update(sched_time)
    elif (update_name := request.args.get("update_item")):
        update_handler.remove_update(update_name)
    elif (blocked_title := request.args.get("notif")):
        cnh.block_article(blocked_title)

    # Run and format updates.
    cdh.s.run(blocking=False)
    cnh.s.run(blocking=False)
    update_handler.format_updates()

    # Process COVID data.
    l_7days_cases = cdh.process_covid_csv_data(cdh.covid_data[ltla])[0]
    n_7days_cases, n_hospital_cases, n_deaths = \
        cdh.process_covid_csv_data(cdh.covid_data[nation])

    return render_template(
        template_name_or_list='index.html',
        title=read_config("dashboard_title")[0],
        favicon=read_config("dashboard_favicon")[0],
        image="Favicon.png",
        location=ltla,
        local_7day_infections=l_7days_cases,
        nation_location=nation,
        national_7day_infections=n_7days_cases,
        hospital_cases=f"Hospital Cases: {str(n_hospital_cases)}",
        deaths_total=f"Total Deaths: {str(n_deaths)}",
        news_articles=cnh.news_articles,
        updates=update_handler.updates)


if __name__ == "__main__":
    app.run()
