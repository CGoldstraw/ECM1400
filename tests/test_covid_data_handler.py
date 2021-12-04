from covid_data_handler import parse_csv_data
from covid_data_handler import read_csv_value
from covid_data_handler import first_non_blank_cell
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import create_covid_update
from covid_data_handler import schedule_covid_updates


def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639


def test_read_csv_value():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert read_csv_value(data[1], 6) == 0
    assert read_csv_value(data[2], 6) == 8_786
    assert read_csv_value(data[100], 4) == 133_896
    row = "0,10,20,30,40,50"
    assert read_csv_value(row, 3) == 30


def test_first_non_blank_cell():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert first_non_blank_cell(data, 4) == 14
    assert first_non_blank_cell(data, 5) == 1
    assert first_non_blank_cell(data, 6) == 2
    data_2 = ["Cats,Dogs,Fish", "1,,3", "2,1,3"]
    assert first_non_blank_cell(data_2, 1) == 2


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)
    assert isinstance(data["Exeter"], list)
    assert isinstance(data["Exeter"][0], str)
    headers = data["Exeter"][0].split(",")
    assert "cumDailyNsoDeathsByDeathDate" in headers
    assert "hospitalCases" in headers
    assert "newCasesBySpecimenDate" in headers


def test_create_covid_update():
    create_covid_update("00:00", "Test", None)


def test_schedule_covid_updates():
    schedule_covid_updates(
        update_interval=10, update_name='update test')
