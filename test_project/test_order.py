from order import create_order


def test_create_order():
    order = create_order(3)

    assert order["quantity"] == 3
    assert order["total"] == 330