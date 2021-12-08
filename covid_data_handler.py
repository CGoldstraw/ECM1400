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

"""Handles requesting and parsing recent COVID data.

Requests and processes recent COVID data from the uk_covid19 API.
Creation and deletion of scheduled updates is also implemented.
"""
import time
import sched
import logging
from datetime import datetime
from uk_covid19 import Cov19API
from config_handler import read_config

covid_data = {}
covid_updates = {}
s = sched.scheduler(time.time, time.sleep)


def parse_csv_data(csv_filename: str) -> list[str]:
    """Reads a csv file and returns it as a list of strings.

    Reads a csv file in the current directory and returns a list of
    rows, where each row is a string.

    Args:
        csv_filename: The name of the csv file.

    Returns:
        A list of strings, each representing a row of the csv file.
    """
    with open(csv_filename, "r", encoding="UTF-8") as csv_file:
        contents = csv_file.read()
        return contents.splitlines()


def read_csv_value(csv_row: str, column: int) -> int:
    """Returns an integer value at a given column in a csv row.

    Args:
        csv_row: The comma separated string to read.
        column: The index of the column to be read.

    Returns:
        The integer value in the specified location if a value exists.
        Returns 0 as a default value if the cell is empty.

    Example:
        >>> row = "0,10,20,30,40,50"
        >>> read_csv_value(row, 3)
        30
    """
    value = csv_row.split(",")[column]
    return int(value if value else 0)


def first_non_blank_cell(csv_lines: list[str], column: int) -> int:
    """Find the first cell with data in a column of a csv file.

    Search a column of a csv file for the first non-empty value
    (excluding the first header row) and return its index. Returns -1
    if there is no cell with data.

    Args:
        csv_lines: Rows of a csv file in a list.
        column: The index of the column to be searched.

    Returns:
        The index of the first row with data for the given column,
        excluding the first header row, or -1 if no data found.

    Example:
        >>> csv_lines = ["Cats,Dogs,Fish", "1,,3", "2,1,3"]
        >>> first_non_blank_cell(csv_lines, 1)
        2
    """
    for i in range(1, len(csv_lines)):
        if read_csv_value(csv_lines[i], column):
            return i
    return -1


def process_covid_csv_data(
        covid_csv_data: list[str]) -> tuple[int, int, int]:
    """Summarises a csv file containing COVID data.

    Takes a csv file containing COVID data, in the format returned
    by the uk_covid19 API, and returns the cases in the last 7 days,
    the current hospital cases, and the cumulative deaths.

    Args:
        covid_csv_data: A csv file containing COVID data, with
        cumulative deaths, hospital cases, and daily cases columns.

    Returns:
        A tuple containing the cases in the last 7 days, the current
        hospital cases, and the total deaths.
    """
    headers = covid_csv_data[0].split(",")
    # Sum of last seven day's cases, excluding the most recent value.
    column = headers.index("newCasesBySpecimenDate")
    row = first_non_blank_cell(covid_csv_data, column) + 1
    week = covid_csv_data[row:row+7]
    week_cases = sum(read_csv_value(day, column) for day in week)

    # Hospital Cases
    column = headers.index("hospitalCases")
    row = first_non_blank_cell(covid_csv_data, column)
    hospital_cases = read_csv_value(covid_csv_data[row], column)

    # Total Deaths
    column = headers.index("cumDailyNsoDeathsByDeathDate")
    row = first_non_blank_cell(covid_csv_data, column)
    total_deaths = read_csv_value(covid_csv_data[row], column)

    return week_cases, hospital_cases, total_deaths


def covid_API_request(
        location: str = "Exeter",
        location_type: str = "ltla") -> dict[str]:
    """Requests current COVID data from the Cov19API for a given area.

    Uses the Cov19API to request the most recent COVID data for
    a given area. Returns data as a list of comma separated strings.

    Args:
        location: The requested COVID data location.
        location_type: The type of area requested ("nation" or "ltla").

    Returns:
        A dictionary containing a csv file containing COVID information
        for an area, indexed by the area's name.
    """
    requested_area = ["areaType="+location_type, "areaName="+location]
    requested_data = {
        "areaCode": "areaCode",
        "areaName": "areaName",
        "areaType": "areaType",
        "date": "date",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    logging.info("Requesting COVID data for %s...", location)
    api = Cov19API(filters=requested_area, structure=requested_data)
    data = api.get_csv()
    covid_data[location] = data.split("\n")[:-1]
    logging.info("COVID data for %s updated.", location)
    return covid_data


def run_covid_update(update_name: str) -> None:
    """Enacts a scheduled update and either repeats or deletes it.

    Updates COVID data for the area specified in config.json, and
    schedules a new update if the update repeats, otherwise the
    update is removed.

    Args:
        update_name: The identifier of the update.
    """
    nation, ltla, interval = read_config(
        "covid_nation", "covid_local", "covid_update_interval_seconds")
    covid_API_request(location=ltla, location_type="ltla")
    covid_API_request(location=nation, location_type="nation")

    logging.info("COVID update '%s' completed.", update_name)
    if covid_updates[update_name]["repeats"]:
        schedule_covid_updates(interval, update_name)
        repeat_log = "COVID update '%s' scheduled to repeat."
        logging.info(repeat_log, update_name)
    else:
        covid_updates.pop(update_name)
        logging.info("COVID update '%s' removed.", update_name)


def create_covid_update(
        update_time: str, update_name: str, repeats: str) -> None:
    """Create and schedule a COVID update for a given time in HH:MM.

    Creates a new update with a given name and repeating information,
    calculates seconds difference between the current time the update
    time, then schedules an update with that delay.

    Args:
        update_time: Time of the update in HH:MM.
        update_name: The identifier of the update.
        repeats: Either None or "repeat".
    """
    update = {"time": update_time, "repeats": repeats}
    covid_updates[update_name] = update
    # Calculate number of seconds until the update.
    schedule_time = datetime.strptime(update_time, "%H:%M")
    current_time = datetime.now()
    seconds = (schedule_time - current_time).seconds
    schedule_covid_updates(seconds, update_name)

    log_message = "%s COVID update '%s' created for %s."
    repeating = "Repeating" if repeats else "Single"
    logging.info(log_message, repeating, update_name, update_time)


def schedule_covid_updates(
        update_interval: int, update_name: str) -> None:
    """Schedules a COVID update in a specified number of seconds.

    Calls a COVID update in a specified number of seconds, and creates
    a new update if the identifier is not found.

    Args:
        update_interval: The number of seconds until the update.
        update_name: The identifier of the update.
    """
    if update_name not in covid_updates:
        covid_updates[update_name] = {"time": "None", "repeats": None}
        logging.warning("Update not found, dummy update created.")

    update = s.enter(update_interval, 1, run_covid_update, update_name)
    covid_updates[update_name]["update"] = update
