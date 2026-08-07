def calculate_shipping(weight_kg):
    """$2.50/kg, free at 50kg or more."""
    if weight_kg >= 50:
        return 0
    return round(weight_kg * 2.0, 2)
