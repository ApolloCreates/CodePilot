from backend.app.demo_target.calculator import calculate_discount


def test_calculate_discount():
    assert calculate_discount(100, 20) == 80
    