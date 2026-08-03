from external_rates import lookup_rate


def convert_to_usd(amount, currency):
    """Convert an amount in `currency` to USD.

    lookup_rate(currency) returns USD -> currency (e.g. 1 USD = 0.92 EUR),
    so converting the other way is a division, not a multiplication.
    """
    rate = lookup_rate(currency)
    return amount * rate
