def is_eligible(age: int, has_id: bool) -> bool:
    if age >= 18 and has_id:
        return True
    return False