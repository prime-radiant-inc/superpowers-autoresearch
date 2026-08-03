"""Stands in for a network round-trip to a currency rates provider."""
import time

_USD_TO_CURRENCY = {"EUR": 0.92, "GBP": 0.79, "JPY": 149.5}


def lookup_rate(currency):
    time.sleep(0.05)  # pretend network latency
    return _USD_TO_CURRENCY[currency]
