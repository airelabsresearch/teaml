from collections import namedtuple

from teaml.value.value import Value

Row = namedtuple('Test', ['input', 'expected'])

def test_value():
    assert 1 == 1
    val = Value(1)
    assert val.value == 1

def test_one():
    result = Value(1) + Value(2)
    assert result.value == 3

# def test_simple_values():
#     for test in [
#         Test('1', 1),
#         Test('1.0', 1),
#         Test('1.1.1', None),
#     ]:
#         result = Value(test.input)
#         assert result.final == test.expected

# def test_percent():
#     result = Value("85%")
#     assert result.final == 0.85
#  make_value("85%")
# make_value("100 MWac")
# make_value([1,2,3])
# make_value('=200*365*1 =73_000 MWh/yr')
# make_value('=Battery Power*Battery Duration =200 MWh').names
# make_value('=Production.Solar Generation*Solar Generation Price*Inflaction Factor = [4_380_000,4_489_500]').names
# make_value('$30/MWh')
# make_value('=1 + range(1,3) =[2,3]').compute({})
# make_value('=range(1,3) =[2,3]').value
# make_value('[2,3]').value