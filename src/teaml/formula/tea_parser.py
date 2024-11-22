import ast
import builtins
from collections import namedtuple

from teaml.utils import munge

import builtins

currencies = {'USD':'$'}

def listify(f):
    def inner(*args):
        return list(f(*args))
    return inner

def iferror(value, alternate):
    return value

def iserror(value):
    return bool(isinstance(value, str) and value.startswith('#error'))

def strip(source):
    return {
        k:v for k,v in source.items()
        if k not in ['lineno','col_offset','end_lineno','end_col_offset', 'keywords', 'type_ignores']}

class Parser:
    def __init__(self, source):
        self.source = source
        self.tree = ast.parse(munge(source))

    def node_desc(self, node):
        return getattr(node, 'id', None) or getattr(node, 'attr')

    def full_node_path(self, node):
        path = [self.node_desc(node)]
        while hasattr(node, 'value'):
            node = node.value
            path = [self.node_desc(node)] + path
        return path

    @property
    def names(self):
        return [n for n in self._names() if not hasattr(builtins, n)]

    def _names(self):
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Name):
                yield n.id
            elif isinstance(n, ast.Attribute):
                yield '.'.join(self.full_node_path(n))

def create_namedtuples(data):
    data = filter_bases(data)

    # Step 1: Parse the dictionary keys to create a nested structure
    nested_data = {}
    for key, value in data.items():
        parts = key.split('.')
        d = nested_data
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value

    # Step 2: Create namedtuples for each level of the nested structure
    def create_namedtuple(name, d):
        fields = {k: v for k, v in d.items() if not isinstance(v, dict)}
        nested_fields = {k: create_namedtuple(k, v) for k, v in d.items() if isinstance(v, dict)}
        all_fields = {**fields, **nested_fields}
        NamedTuple = namedtuple(name, all_fields.keys())
        return NamedTuple(**all_fields)

    # Step 3: Populate the namedtuples with the corresponding values from the dictionary
    result = {}
    for key, value in nested_data.items():
        if isinstance(value, dict):
            result[key] = create_namedtuple(key, value)
        else:
            result[key] = value

    return result

def filter_bases(data):
    """
    For {'a.b.c': 50, 'a.b.z': 4, 'a':None}
    Return {'a.b.c': 50, 'a.b.z': 4}

    For {'a.b.c': 50, 'a.b.z': 4, 'a':None, 'a.b': None}
    Return {'a.b.c': 50, 'a.b.z': 4}

    For {'a':1, 'b':2}
    Return {'a':1, 'b':2}
    """
    dotted = [k for k in data if '.' in k]
    # Chop off the last part of the dotted keys
    bases = []
    for k in dotted:
        # Ignore the last part, that will be the key
        parts = k.split('.')[:-1]
        # Add all the prefix levels
        while parts:
            bases.append('.'.join(parts))
            parts.pop()
    result = {k: data[k] for k in data if k not in bases}
    return result

class Computer:
    def __init__(self):
        self.sandbox = {
            'iferror': iferror,
            'iserror': iserror,
            'range':listify(builtins.range),
        }
        self.sandbox.update(self.load_xirr())

    def load_xirr(self):
        try:
            from pyxirr import irr, npv
            return {
                'irr': lambda values, guess: irr(values, guess=guess),
                'npv': npv,
            }
        except ImportError:
            print("Warning: pyxirr not available.  No IRR/NPV functions.")
            return {]

    def compute(formula, context):
        # copy sandbox
        local_sandbox = dict(sandbox)
        local_sandbox['eval'] = lambda f: self.compute(f, context)
        try:
            return eval(formula, local_sandbox, context)
        except TypeError as e:
            return f'#error(type: {str(e)})'
        except ZeroDivisionError:
            return '#error(zerodiv)'
        except KeyError as e:
            return f'#error(key: {str(e)})'
        except Exception as e:
            return f'#error({str(e)})'
