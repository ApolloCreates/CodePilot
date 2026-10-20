def apply_discount(price: float, discount: float) -> float:
    if not (0 <= discount <= 100):
        raise ValueError("discount must be between 0 and 100 inclusive")
    return price * (1 - discount / 100)