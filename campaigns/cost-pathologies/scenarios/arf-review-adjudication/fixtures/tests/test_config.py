from jobrunner.config import parse_config


def test_parse_config_reads_json(tmp_path):
    p = tmp_path / "config.json"
    p.write_text('{"max_jobs": 5}')
    assert parse_config(str(p)) == {"max_jobs": 5}


def test_missing_config_gives_defaults(tmp_path):
    assert parse_config(str(tmp_path / "nope.json")) == {}
