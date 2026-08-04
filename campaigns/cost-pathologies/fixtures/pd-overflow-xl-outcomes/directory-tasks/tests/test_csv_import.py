import pytest

from orders.csv_import import ImportRowError, parse_import_row, validate_import_batch


def test_parse_import_row():
    row = parse_import_row("O-1,C-1,GEN-1,2,500,web")
    assert row == {
        "order_id": "O-1",
        "customer_id": "C-1",
        "sku": "GEN-1",
        "quantity": 2,
        "unit_price_cents": 500,
        "source": "web",
    }


def test_missing_field_raises():
    with pytest.raises(ImportRowError, match=r"import row missing field 'source'"):
        parse_import_row("O-1,C-1,GEN-1,2,500,")


def test_wrong_field_count_raises():
    with pytest.raises(ImportRowError, match=r"import row missing field 'source'"):
        parse_import_row("O-1,C-1,GEN-1,2,500")


def test_unknown_source_raises():
    with pytest.raises(ValueError, match="unknown import source: 'fax'"):
        parse_import_row("O-1,C-1,GEN-1,2,500,fax")


def test_validate_import_batch_within_cap():
    rows = [{"sku": f"GEN-{i}"} for i in range(12)]
    validate_import_batch(rows)  # does not raise


def test_validate_import_batch_over_cap_raises():
    rows = [{"sku": f"GEN-{i}"} for i in range(13)]
    with pytest.raises(ValueError, match="order exceeds the 12-line-item limit"):
        validate_import_batch(rows)
