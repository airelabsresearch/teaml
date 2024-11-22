from collections import namedtuple
import yaml
import pytest

import teaml as tml
from teaml.node import (
    Node,
    NodeInt,
    NodeNone,
    NodeError,
    NodeString,
    parse_string,
)

Row = namedtuple('Test', ['input', 'expected'])
tests = [
    Row(123, 123),
    Row('123', 123),
    Row('123.0', 123.0),
    Row('=a+b=3', 3),
    Row('=a+b=[1,2,3]', [1,2,3]),
    Row('123 Kg', 123),
]

def test_simple():
    for test in tests:
        assert Node.new(test.input) == test.expected

def test_empty():
    node = Node.new('empty')
    assert node.as_dict == {
        'formula': None,
        'key': None,
        'path': [],
        'type': NodeString,
        'value': 'empty'}

def test_path_to_key():
    node = Node.new(123, path=['a', 'b', 'c'])
    assert node.as_dict == {
        'formula': None,
        'key': 'a.b.c',
        'path': ['a', 'b', 'c'],
        'type': NodeInt,
        'value': 123}

def test_formula():
    node = Node.new(123, formula='=a+b')
    assert node.as_dict == {
        'formula': '=a+b',
        'key': None,
        'path': [],
        'type': NodeInt,
        'value': 123}

def test_error():
    node = parse_string('=1/0=#error: division by zero')
    assert node.as_dict == {
        'formula': '=1/0',
        'key': [],
        'path': [],
        'type': NodeError,
        'value': '#error: division by zero'}