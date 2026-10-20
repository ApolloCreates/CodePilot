from client import get_timeout


def test_get_timeout():
    assert get_timeout() == 30