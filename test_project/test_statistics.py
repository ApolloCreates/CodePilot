from statistics import calculate_average


def test_average_of_numbers():
    assert calculate_average([10, 20, 30]) == 20


def test_average_of_empty_list():
    assert calculate_average([]) == 0