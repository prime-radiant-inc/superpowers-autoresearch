LEDGER_ENTRY_CODES = {
    "received": "AR-PEND",
    "shipped": "AR-REV",
    "cancelled": "AR-VOID",
    "refunded": "AR-CREDIT",
}


def ledger_code_for_status(order_status):
    if order_status not in LEDGER_ENTRY_CODES:
        raise ValueError(f"no ledger code for order status: {order_status!r}")
    return LEDGER_ENTRY_CODES[order_status]
