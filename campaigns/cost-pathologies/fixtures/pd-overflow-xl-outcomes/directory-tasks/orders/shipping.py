MAX_SHIPMENT_WEIGHT_GRAMS = 25000

SHIPPING_RATES_CENTS = {
    "Z1": {"light": 500, "medium": 900, "heavy": 1500},
    "Z2": {"light": 700, "medium": 1200, "heavy": 2000},
    "Z3": {"light": 900, "medium": 1600, "heavy": 2600},
}


def _weight_bracket(weight_grams):
    if weight_grams <= 2000:
        return "light"
    if weight_grams <= 10000:
        return "medium"
    return "heavy"


def compute_shipping_cost(weight_grams, zone):
    if weight_grams > MAX_SHIPMENT_WEIGHT_GRAMS:
        raise ValueError(
            f"shipment of {weight_grams}g exceeds the maximum supported weight "
            f"of {MAX_SHIPMENT_WEIGHT_GRAMS}g"
        )
    if zone not in SHIPPING_RATES_CENTS:
        raise ValueError(f"unknown shipping zone: {zone!r}")
    return SHIPPING_RATES_CENTS[zone][_weight_bracket(weight_grams)]
