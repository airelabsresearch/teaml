
from collections import namedtuple

from teaml.formula.tea_parser import computer, create_namedtuples, filter_bases
from teaml.utils import munge

Row = namedtuple('Test', ['input', 'expected'])

simple_tests = [
    Row('abc+sum(range(1,3))', ['abc']),
    Row('abc.ghi + a.b.c', ['abc.ghi', 'a.b.c', 'abc', 'a.b', 'a']),
]

def test_simple_parse():
    for test in simple_tests:
        p = computer.parse(test.input)
        assert p.names == test.expected, f"Expected {test.expected}, got {p.names}"

def test_simple_eval():
    assert eval('abc+sum(range(1,3))', {'abc': 1}) == 4

def test_prefix_bad():
    p = computer.parse(munge('Solar Capacity*Solar Capacity Factor'))
    assert p.names == ['SolarCapacity', 'SolarCapacityFactor']

def test_fakenames():
    context = {'a.b.c': 50, 'a.b.z': 4}
    context = create_namedtuples(context)
    assert context['a'].b.c == 50
    assert context['a'].b.z == 4

def test_filter_bases():
    context = {'a.b.c': 50, 'a.b.z': 4, 'a':None}
    context = filter_bases(context)
    assert context == {'a.b.c': 50, 'a.b.z': 4}

def test_filter_bases_second():
    context = {
        'a.b.c': 50,
        'a.b.z': 4,
        'a':None,
        'a.b': None}
    context = filter_bases(context)
    assert context == {'a.b.c': 50, 'a.b.z': 4}

def test_filter_bases_101():
    # =Operating Cash Flow + Production Tax Credits + Annual.Operating Expenses.Tax Benefit
    context = {
        'Annual.OperatingExpenses.TaxBenefit': 1,
        'Annual.OperatingExpenses': None,
        'Annual': None}
    context = filter_bases(context)
    assert context == {
        'Annual.OperatingExpenses.TaxBenefit': 1,
    }

def test_fakenames_nesting():
    context = {'a.b.c': 50, 'a.b.z': 4, 'a':None}
    context = create_namedtuples(context)
    assert context['a'].b.c == 50
    assert context['a'].b.z == 4

eval_tests = [
    Row('-c+1', -2),
    Row('range(1,3)', [1, 2]),
    Row('sum(range(1,3))', 3),
    Row('a+b+c',6),
    Row('irr(irr_range, 0.1)', 0.7613778285466168),
    Row('npv(0.1, npv_range)', -67_954_147.42299025),
    Row('1/0', '#error(zerodiv)'),
    Row('eval("1/0")', '#error(zerodiv)'),
    Row('iserror(eval("1/0"))', True),
    Row('iferror(eval("4/2"), 0)', 2),
    Row('iferror(eval("4/0"), 0)', '#error(zerodiv)'),
    Row('max(1,3)', 3),
    Row('min(1,3)', 1),
    Row('round(3.14159, 2)', 3.14),
    Row('roundup(10/9, 0)', 2),
    Row('-pmt(0.1, 25, 1)', 0.11016807219002082),
    Row('sumif([1,2,3], ["n", "y", "y"], "y")', 5),
    Row('concat("a", "b")', 'ab'),
    Row('IF(b<3,1,2)', 1),
    Row('-pmt(0.1, 25, broken)', "#error(#error(upstream failure))"),
    Row('irr(irr_range, broken)', "#error(type argument guess:must be real number, not str)"),
    Row('npv(0.1, broken)', "#error(type argument amounts:must be real number, not str)"),
]

eval_symbols = {
    'a': 1,
    'b': 2,
    'c': 3,
    'irr_range': [-1, 0, 1, 2, 3],
    'npv_range': [-115_000_000, 17_853_058, 20_920_596, 18_003_174],
    'broken': '#error(upstream failure)',
}

def test_evals():
    for test in eval_tests:
        result = computer.compute(test.input, eval_symbols)
        assert result == test.expected, f"Test: {test.input} Expected {test.expected} got: {result}"
