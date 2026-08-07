"""Job handlers, one function per job kind."""


def handle_email(payload):
    to = payload.get("to", "")
    subject = payload.get("subject", "")
    return f"email:{to}:{subject}"


def handle_webhook(payload):
    url = payload.get("url", "")
    return f"webhook:{url}"


def handle_cleanup(payload):
    older_than = payload.get("older_than_days", 30)
    return f"cleanup:{older_than}"
