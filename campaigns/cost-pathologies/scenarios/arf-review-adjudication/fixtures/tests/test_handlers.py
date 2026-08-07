from jobrunner import handlers


def test_email_handler_formats_result():
    assert handlers.handle_email({"to": "x@y.z", "subject": "s"}) == "email:x@y.z:s"


def test_cleanup_handler_defaults_to_30_days():
    assert handlers.handle_cleanup({}) == "cleanup:30"
