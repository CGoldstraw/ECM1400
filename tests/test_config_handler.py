from config_handler import read_config


def test_read_config():
    data = read_config("news_API_key", "covid_nation", "covid_local")
    assert len(data) == 3
