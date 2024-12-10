from collections import namedtuple

from teaml.utils import sanitize_formula

Row = namedtuple('Test', ['input', 'expected'])

def test_sanitize_formula():
    for row in [
        Row(
            "'Sheet 1'!A1 + '123Sheet - 2'!B2 * 'Invalid!Name'!C3",
            "Sheet1.A1+Sheet2.B2*InvalidName.C3"),
        Row("A B C.dd + a.b.c", "ABC.dd+a.b.c"),
    ]:
        assert sanitize_formula(row.input) == row.expected
