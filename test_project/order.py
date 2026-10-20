from pricing import calculate_total


def create_order(quantity: int) -> dict:
    total = calculate_total(quantity)

    return {
        "quantity": quantity,
        "total": total,
    }