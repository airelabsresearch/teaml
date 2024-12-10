from collections import namedtuple

import yaml
import pytest

import teaml as tml
from teaml.container import find_container, PathMatch

def container1():
    return yaml.safe_load('''\
outer:
  inputs:
    mixed level:
      capacity: 300
      capacity value: 100
  outputs:
    capacity: 200
''')

def container2():
    return yaml.safe_load('''\
a:
  b:
    c:
      d: 300
    d: 200
''')


def test_basic_access():
    data = container1()
    assert find_container(data, 'mixed.capacity').value == 300
    assert find_container(data, 'inp.capacity').value == 300
    assert find_container(data, 'outputs.capacity').value == 200
    assert find_container(data, 'capacity value').value == 100

    with pytest.raises(ValueError):
        find_container(data, 'capacit')

def test_path():
    data = container1()
    assert find_container(data, 'mixed.capacityv').path == ['outer', 'inputs', 'mixed level', 'capacity value']

def test_jumpers():
    data = container2()
    assert find_container(data, 'a.b.c.d').value == 300
    assert find_container(data, 'c.d').value == 300
    assert find_container(data, 'b.d').value == 200

def test_path_match():
    Test = namedtuple('Test', ['path', 'search', 'pattern', 'score'])
    for test in [
        Test(['a', 'b', 'c', 'd'], ['c', 'd'], '__==', 200),
        Test(['a', 'b', 'c', 'd'], ['b', 'd'], '_=_=', 190),
        Test(['a', 'b', 'c', 'de'], ['b', 'd'], '_=_/', 90),
    ]:
        pm = PathMatch(path=test.path, search=test.search)
        assert pm.pattern == test.pattern
        assert pm.score == test.score

def test_ambiguous():
    data = container1()
    with pytest.raises(ValueError):
        find_container(data, 'cap')