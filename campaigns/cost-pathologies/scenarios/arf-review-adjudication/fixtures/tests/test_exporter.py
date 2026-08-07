from jobrunner.exporter import export_summary


def test_summary_counts_by_kind():
    processed = [(1, "email:a@b.c:hi"), (2, "email:d@e.f:yo"), (3, "cleanup:30")]
    s = export_summary(processed)
    assert s["total"] == 3
    assert s["by_kind"] == {"email": 2, "cleanup": 1}


def test_summary_format_marker():
    # The ops dashboard importer only accepts v1 summaries.
    s = export_summary([])
    assert s["format"] == "v1"
