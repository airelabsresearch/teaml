
from collections import namedtuple

from teaml.formula.tea_parser import Parser, create_namedtuples, filter_bases, compute
from teaml.utils import munge

Row = namedtuple('Test', ['input', 'expected'])

simple_tests = [
    Row('abc+sum(range(1,3))', ['abc']),
    Row('abc.ghi + a.b.c', ['abc.ghi', 'a.b.c', 'abc', 'a.b', 'a']),
]

def test_simple_parse():
    for test in simple_tests:
        p = Parser(test.input)
        assert p.names == test.expected, f"Expected {test.expected}, got {p.names}"

def test_simple_eval():
    assert eval('abc+sum(range(1,3))', {'abc': 1}) == 4

def test_prefix_bad():
    p = Parser(munge('Solar Capacity*Solar Capacity Factor'))
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
]

eval_symbols = {
    'a': 1,
    'b': 2,
    'c': 3,
    'irr_range': [-1, 0, 1, 2, 3],
    'npv_range': [-115_000_000, 17_853_058, 20_920_596, 18_003_174],
}

def test_evals():
    for test in eval_tests:
        result = compute(test.input, eval_symbols)
        assert result == test.expected, f"Test: {test.input} Expected {test.expected} got: {result}"
