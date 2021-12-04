from update_handler import format_update


def test_format_update():
    update = {"time": "01:23", "repeats": "repeat"}
    formatted = "01:23, Updates Covid & News, Repeats"
    assert format_update(update, True, True) == formatted

    update = {"time": "12:34", "repeats": None}
    formatted = "12:34, Updates News, Doesn't Repeat"
    assert format_update(update, False, True) == formatted
    
