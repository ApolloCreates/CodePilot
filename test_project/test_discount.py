from discount import apply_discount


def test_normal_discount():
    assert apply_discount(100, 20) == 80


def test_zero_discount():
    assert apply_discount(100, 0) == 100


def test_discount_over_100_is_rejected():
    try:
        apply_discount(100, 120)
        assert False, "Expected ValueError"
    except ValueError:
        pass