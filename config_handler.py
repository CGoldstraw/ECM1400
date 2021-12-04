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

"""Handles reading and validating fields in the config file."""
import json
import logging
from typing import Any


def validate_field(field: str, value: Any) -> Any:
    """Type checks a given config field.

    Compare a field value's type with the expected type for that field.
    Return the value if the type matches, otherwise return the default
    value for that field.

    Args:
        field: The name of the field.
        value: The value stored in that field.

    Returns:
        Either the value of the field or the default value of the
        field, depending on whether the value is of the expected type.
    """
    expected_types = {
        "dashboard_title": str,
        "dashboard_favicon": str,
        "covid_nation": str,
        "covid_local": str,
        "covid_update_interval_seconds": int,
        "news_API_key": str,
        "news_country_code": str,
        "news_update_interval_seconds": int,
        "news_search_terms": str
    }

    default_values = {
        "dashboard_title": "COVID-19 Dashboard",
        "dashboard_favicon": "https://i.ibb.co/7nYCWzN/Favicon.png",
        "covid_nation": "England",
        "covid_local": "Exeter",
        "covid_update_interval_seconds": 86400,
        "news_API_key": "",
        "news_country_code": "gb",
        "news_update_interval_seconds": 86400,
        "news_search_terms": "Covid COVID-19 coronavirus"
    }
    if isinstance(value, expected_types[field]):
        return value

    type_error_log = "Config field '%s' invalid type. %s should be: %s"
    actual = type(value).__name__
    expected = expected_types[field].__name__
    logging.warning(type_error_log, field, actual, expected)

    default_value = default_values[field]
    replace_log = "Invalid config value '%s' replaced with '%s'"
    logging.warning(replace_log, value, default_value)
    return default_value



def read_config(*fields: str) -> list[str]:
    r"""Reads the config file for given fields.

    Open config.json in the current directory and return the data in
    the fields specified in the arguments.

    Args:
        *fields: Variable number of fields to return from config.json.

    Returns:
        A list containing the data inside the fields specified by
        the fields argument, in the order that the fields were
        given in. Returns None for any fields with the wrong type.
    """
    with open("config.json", "r", encoding="UTF-8") as config_file:
        config = json.load(config_file)

    return [validate_field(field, config[field]) for field in fields]
