from formatter import format_user


def test_format_user():
    assert format_user("Mohit", 21) == "Mohit is 21 years old"