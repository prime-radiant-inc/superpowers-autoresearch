from pricing import calc_line_totals, calc_total


def test_calc_line_totals():
    assert calc_line_totals([(10, 1), (5, 2), (2, 3)]) == [10, 10, 6]


def test_calc_total():
    assert calc_total([(10, 1), (5, 2), (2, 3)]) == 26
