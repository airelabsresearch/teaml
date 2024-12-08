import ast
import builtins
import math
from collections import namedtuple

from teaml.utils import munge

currencies = {'USD':'$'}

def listify(f):
    def inner(*args):
        return list(f(*args))
    return inner

def concat(*args):
    return ''.join(str(a) for a in args)

def iferror(value, alternate):
    return value

def iserror(value):
    return bool(isinstance(value, str) and value.startswith('#error'))

def strip(source):
    return {
        k:v for k,v in source.items()
        if k not in ['lineno','col_offset','end_lineno','end_col_offset', 'keywords', 'type_ignores']}

def roundup(number, digits=0):
    multiplier = 10 ** digits
    return math.ceil(number * multiplier) / multiplier

def sumif(values_range, criteria_range, criterion):
    """Implements Excel's SUMIF in Python."""
    return sum(value for crit, value in zip(criteria_range, values_range) if crit == criterion)

def IF(condition, true_value, false_value):
    """Basic excel-like IF"""
    if condition:
        return true_value
    return false_value

class Parser:
    def __init__(self, source, sandbox):
        self.source = source
        self.sandbox = sandbox
        self.tree = ast.parse(munge(source))

    def node_desc(self, node):
        return getattr(node, 'id', None) or getattr(node, 'attr')

    def full_node_path(self, node):
        path = [self.node_desc(node)]
        while hasattr(node, 'value'):
            node = node.value
            path = [self.node_desc(node)] + path
        return path

    def should_exclude(self, name):
        return name in self.sandbox or hasattr(builtins, name)

    @property
    def names(self):
        return [n for n in self._names() if not self.should_exclude(n)]

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

def unsupported(*args):
    raise NotImplementedError("Unsupported operation")

class Computer:
    def __init__(self):
        self.sandbox = {
            'concat': concat,
            'iferror': iferror,
            'irr': unsupported,
            'iserror': iserror,
            'pmt': unsupported,
            'npv': unsupported,
            'range':listify(builtins.range),
            'roundup': roundup,
            'sumif': sumif,
            'IF':IF,
        }
        self.sandbox.update(self.load_xirr())

    def load_xirr(self):
        try:
            import pyxirr as xfn
            # from pyxirr import irr, npv, pmt
            return {
                'irr': lambda values, guess: xfn.irr(values, guess=guess),
                'npv': xfn.npv,
                'pmt': xfn.pmt,
            }
        except ImportError:
            print("Warning: pyxirr not available.  No IRR/NPV functions.")
            return {}

    def parse(self, source):
        return Parser(source, sandbox=self.sandbox)

    def compute(self, formula, context):
        """
        Compute a formula using the given context and a sandbox.
        """
        # copy sandbox
        local_sandbox = dict(self.sandbox)
        local_sandbox['eval'] = lambda f: self.compute(f, context)
        try:
            # TODO: ast.literal_eval
            return eval(formula, local_sandbox, context)
        except TypeError as e:
            return f'#error(type: {str(e)})'
        except ZeroDivisionError:
            return '#error(zerodiv)'
        except KeyError as e:
            return f'#error(key: {str(e)})'
        except Exception as e:
            return f'#error({str(e)})'

computer = Computer()
