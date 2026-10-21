BASE_PRICE = 100
SERVICE_FEE = 30


def calculate_total(quantity: int) -> float:
    return BASE_PRICE * quantity + SERVICE_FEE