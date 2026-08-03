from abc import abstractmethod

MAX_LINE_ITEMS = 12
CURRENCY = "USD"


class Currency:
    code = "USD"

    @abstractmethod
    def format(self, amount_cents):
        raise NotImplementedError


class USDCurrency(Currency):
    code = "USD"

    def format(self, amount_cents):
        return f"${amount_cents / 100:.2f}"


class CurrencyRegistry:
    _currencies = {"USD": USDCurrency()}

    @classmethod
    def get(cls, code):
        return cls._currencies[code]


def compute_total(line_items):
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return sum(item["unit_price_cents"] * item["quantity"] for item in line_items)
