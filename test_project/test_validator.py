from validator import is_eligible


def test_underage_without_id_is_not_eligible():
    assert is_eligible(16, False) is False


def test_adult_without_id_is_not_eligible():
    assert is_eligible(20, False) is False