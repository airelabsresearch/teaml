from collections import namedtuple
from typing import List, Optional

from teaml.nodepath import NodePath
from teaml.value.value import Value
from teaml.utils import single_type, munge
from teaml.formula.tea_parser import Parser

class Node:
    @property
    def path(self) -> List[str]:
        return getattr(self, '_path', [])

    @path.setter
    def path(self, value: List[str]):
        value = value or []
        assert isinstance(value, list), f"Invalid path: {value}"
        self._path = value

    @property
    def key(self) -> str:
        return getattr(self, '_key', [])

    @key.setter
    def key(self, value: str):
        value = munge(value)
        assert value is None or isinstance(value, str), f"Invalid key: {value}"
        self._key = value

    @property
    def needs_compute(self) -> bool:
        if not self.formula:
            return False
        return isinstance(self, NodeNone)

    @needs_compute.setter
    def needs_compute(self, value: bool):
        assert isinstance(value, bool)
        self._needs_compute = value

    @property
    def formula(self) -> List[str]:
        return getattr(self, '_formula', None)

    @property
    def parser(self):
        return Parser(munge(self.formula)) if self.formula is not None else None

    @property
    def references(self):
        return self.parser.names if self.parser is not None else []

    @property
    def name(self) -> Optional[str]:
        return self.path[-1] if self.path else None

    @property
    def value(self):
        return str(self)

    @property
    def is_error(self):
        return isinstance(self, NodeError)

    @property
    def is_none(self):
        return isinstance(self, NodeNone)

    @property
    def children(self):
        return []

    # def compute(self):
    #     if self.formula is None:
    #         return self.value

    @property
    def detail(self):
        return f"""\
Value: {repr(self.value)}
Type: {type(self.value)}
Path: {self.path}
Key: {self.key}
Formula: {self.formula}
"""

    @property
    def as_dict(self):
        return {
            'value': self.value,
            'type': type(self),
            'path': self.path,
            'key': self.key,
            'formula': self.formula,
        }

    @property
    def raw(self):
        if not self.formula:
            return self.value
        return f"{self.formula} ={self.value}"

    @classmethod
    def new(cls, data, key=None, path=None, formula=None):
        if key is None and isinstance(path, list):
            key = '.'.join(path)
        if key is not None:
            key = munge(key)
        if formula is not None:
            if not formula.startswith('='):
                raise ValueError(f"Invalid formula: {formula}")
            data = f"{formula}={data}"
        try:
            return _new_node(data, key, path)
        except ValueError as e:
            print(type(data))
            print(f"Error: {repr(data)}")
            raise e

def _new_node(data, key=None, path=None):
    def fail(d):
        raise ValueError(f'Unknown data type: {d}')
    node = {
        dict: NodeDict,
        float: NodeFloat,
        int: NodeInt,
        list: NodeRange,
        str: parse_string,
        type(None): lambda _: NodeNone(),
    }.get(type(data), fail)(data)
    node.key = key
    node.path = path
    return node

def parse_string(string) -> Node:
    string = string.strip()
    if string.startswith('='):
        return parse_formula(string)
    if string.startswith('[') and string.endswith(']'):
        return parse_range(string)
    if string.endswith('%'):
        num = as_num(string.rstrip('%'))

        if num is not None:
            num = num / 100.0
            return NodeFloat(num)

    if string.startswith('$'):
        # TODO: remember this is a currency?
        string = string.lstrip('$')

    # Look for "NUM UNITS"
    parts = string.split(' ')
    if len(parts) == 2:
        num = as_num(parts[0])
        return Node.new(num)

    # Look for "NUM/UNITS"
    # TODO: remember this is a rate?
    parts = string.split('/', 1)
    if len(parts) == 2:
        num = as_num(parts[0])
        return Node.new(num)

    num = as_num(string)
    if num is not None:
        return Node.new(num)

    return NodeString(string)

def parse_formula(string) -> Node:
    assert string.startswith('=')
    parts = string[1:].split('=', 1)
    formula = parts[0].strip()
    if len(parts) > 1:
        value = parts[1].strip()
        if value.startswith('#'):
            node = NodeError(value)
        else:
            node = parse_string(value)
    else:
        node = NodeNone()
    # node = parse_string(parts[1].strip()) if len(parts) > 1 else NodeNone()
    node._formula = '=' + formula
    return node

def as_num(value):
    """
    Convert a value to a number if possible

    If int() and float() are the same value, return an int
    """
    int_value = None
    float_value = None
    try:
        int_value = int(value)
    except ValueError:
        pass
    try:
        float_value = float(value)
    except ValueError:
        pass
    if int_value is None and float_value is None:
        return None
    if int_value == float_value:
        return int_value
    return float_value

def parse_range(string) -> Node:
    assert string.startswith('[') and string.endswith(']')
    parts = string[1:-1].split(',')
    nums = [as_num(p) for p in parts]
    if single_type(nums) in (float, int):
        return NodeRange(nums)
    return NodeRange(parts)

class NodeInt(int, Node):
    @property
    def value(self):
        return int(self)

class NodeFloat(float, Node):
    @property
    def value(self):
        return float(self)

class NodeNone(Node):
    @property
    def value(self):
        return None

class NodeRange(list, Node):
    @property
    def value(self):
        return self[:]

class NodeString(str, Node):
    @property
    def value(self):
        return str(self)

class NodeDict(dict, Node):
    @property
    def children(self):
        return [
            Node(value, self.path + [key])
            for key, value in self.items()]

    @property
    def value(self):
        return None

class NodeError(str, Node):
    @property
    def value(self):
        return str(self)
